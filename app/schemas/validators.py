"""Row progression DSL parsing, compression, statistics, and venue diff helpers."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from math import log2
from typing import Literal, TypedDict

from app.schemas.row import RowOut, RowProgression
from app.schemas.section import SectionInput, SectionOut
from app.schemas.venue import Venue, VenueOut

ATOM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
LETTER_RE = re.compile(r"^([A-Z])\1*$")
NUMBER_RE = re.compile(r"^(0|[1-9]\d*)$")

CodeType = Literal["numeric", "alphabetic", "mixed"]
RangeFamily = tuple[Literal["numeric", "letter"], int, int]


class StatsData(TypedDict):
    code_type: CodeType
    total_rows: int
    unique_row_count: int
    unique_position_count: int
    unique_names: set[str]
    name_entropy: float
    segment_count: int


class RowPositionDelta(TypedDict):
    a: int | None
    b: int | None


VenueDiff = dict[str, dict[str, RowPositionDelta]]


def _validate_atom(name: str) -> str:
    if not name:
        raise ValueError("Row code cannot be empty.")
    if not ATOM_RE.fullmatch(name):
        raise ValueError(f"Invalid row code '{name}'.")
    return name


def _parse_step(raw_step: str, raw_segment: str) -> int:
    if not NUMBER_RE.fullmatch(raw_step):
        raise ValueError(f"Invalid positive step in segment '{raw_segment}'.")
    step = int(raw_step)
    if step <= 0:
        raise ValueError(f"Step must be positive in segment '{raw_segment}'.")
    return step


def _inclusive_range(start: int, end: int, step: int) -> range:
    direction = 1 if end >= start else -1
    return range(start, end + direction, step * direction)


def _letter_ordinal(code: str) -> int:
    return ord(code[0]) - ord("A") + 1


def _letter_code(ordinal: int, length: int) -> str:
    return chr(ord("A") + ordinal - 1) * length


def _range_family(name: str) -> RangeFamily | None:
    if NUMBER_RE.fullmatch(name):
        return ("numeric", 0, int(name))
    if LETTER_RE.fullmatch(name):
        return ("letter", len(name), _letter_ordinal(name))
    return None


def _expand_numeric(start: str, end: str, step: int) -> list[str]:
    return [str(value) for value in _inclusive_range(int(start), int(end), step)]


def _expand_letters(start: str, end: str, step: int) -> list[str]:
    length = len(start)
    ordinals = _inclusive_range(_letter_ordinal(start), _letter_ordinal(end), step)
    return [_letter_code(ordinal, length) for ordinal in ordinals]


def _range_codes(start: str, end: str, step: int) -> list[str]:
    if NUMBER_RE.fullmatch(start) and NUMBER_RE.fullmatch(end):
        return _expand_numeric(start, end, step)

    if LETTER_RE.fullmatch(start) and LETTER_RE.fullmatch(end):
        if len(start) != len(end):
            raise ValueError(
                f"Invalid slice '{start}:{end}'. Letter ranges must use the same "
                "repeated-letter length."
            )
        return _expand_letters(start, end, step)

    raise ValueError(
        f"Invalid slice '{start}:{end}'. Ranges require matching numeric or pure "
        "repeated-letter codes."
    )


def _validate_unique_rows(rows: Sequence[RowOut]) -> None:
    names = [row.name for row in rows]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate row names: {', '.join(duplicates)}")


def parse_code(code: str) -> list[RowOut]:
    """Expand a compact row progression code into concrete rows."""

    if not code.strip():
        raise ValueError("Row progression code cannot be empty.")

    position = 1
    rows: list[RowOut] = []

    for raw_segment in code.split(","):
        segment = raw_segment.strip()
        if not segment:
            raise ValueError("Row progression code contains an empty segment.")

        is_gap = segment.endswith("!")
        if is_gap:
            segment = segment[:-1].strip()

        if not segment:
            raise ValueError(f"Gap segment '{raw_segment}' is missing a row code.")
        if "!" in segment:
            raise ValueError(f"Gap marker must end segment '{raw_segment}'.")

        if "=" in segment:
            if ":" in segment:
                raise ValueError(
                    f"Equivalent segment '{raw_segment}' must contain atomic row codes."
                )
            names = [_validate_atom(name.strip()) for name in segment.split("=")]
            if len(names) < 2:
                raise ValueError(f"Malformed equivalent segment '{raw_segment}'.")
            if len(set(names)) != len(names):
                raise ValueError(f"Duplicate row names in '{raw_segment}'.")
            if not is_gap:
                rows.extend(RowOut(name=name, position=position) for name in names)
            position += 1
            continue

        parts = [part.strip() for part in segment.split(":")]
        if len(parts) == 1:
            name = _validate_atom(parts[0])
            if not is_gap:
                rows.append(RowOut(name=name, position=position))
            position += 1
            continue

        if len(parts) not in {2, 3}:
            raise ValueError(f"Malformed range segment '{raw_segment}'.")

        start = _validate_atom(parts[0])
        end = _validate_atom(parts[1])
        step = _parse_step(parts[2], raw_segment) if len(parts) == 3 else 1

        for name in _range_codes(start, end, step):
            if not is_gap:
                rows.append(RowOut(name=name, position=position))
            position += 1

    _validate_unique_rows(rows)
    return rows


def parse_bulk(codes: Sequence[str]) -> list[RowProgression]:
    return [RowProgression(code=code, rows=parse_code(code)) for code in codes]


def _code_type(name: str) -> CodeType:
    if NUMBER_RE.fullmatch(name):
        return "numeric"
    if LETTER_RE.fullmatch(name):
        return "alphabetic"
    return "mixed"


def _gap_segment(start_position: int, count: int) -> str:
    if count <= 0:
        raise ValueError("Gap count must be positive.")
    if count == 1:
        return f"{start_position}!"
    return f"{start_position}:{start_position + count - 1}!"


def _can_extend_slice(
    previous_name: str,
    next_name: str,
    current_step: int | None,
) -> tuple[bool, int | None]:
    previous = _range_family(previous_name)
    next_value = _range_family(next_name)
    if previous is None or next_value is None:
        return False, current_step
    if previous[:2] != next_value[:2]:
        return False, current_step

    delta = next_value[2] - previous[2]
    if delta == 0:
        return False, current_step
    if current_step is None:
        return True, delta
    return delta == current_step, current_step


def compress_rows(rows: Sequence[RowOut]) -> str:
    """Compress rows into a canonical DSL string that preserves parse semantics."""

    if not rows:
        return ""

    _validate_unique_rows(rows)
    ordered = sorted(rows, key=lambda row: row.position)
    groups: list[tuple[int, list[str]]] = []

    for row in ordered:
        if groups and groups[-1][0] == row.position:
            groups[-1][1].append(row.name)
        else:
            groups.append((row.position, [row.name]))

    out: list[str] = []
    expected_position = 1
    index = 0

    while index < len(groups):
        position, names = groups[index]
        if position < expected_position:
            raise ValueError("Rows must not move backwards in position order.")
        if position > expected_position:
            out.append(_gap_segment(expected_position, position - expected_position))
            expected_position = position

        if len(names) > 1:
            out.append("=".join(names))
            expected_position = position + 1
            index += 1
            continue

        run_names = [names[0]]
        current_step: int | None = None
        lookahead = index + 1

        while lookahead < len(groups):
            next_position, next_names = groups[lookahead]
            if next_position != position + len(run_names) or len(next_names) != 1:
                break

            can_extend, next_step = _can_extend_slice(
                run_names[-1],
                next_names[0],
                current_step,
            )
            if not can_extend:
                break

            current_step = next_step
            run_names.append(next_names[0])
            lookahead += 1

        if len(run_names) > 1:
            segment = f"{run_names[0]}:{run_names[-1]}"
            if current_step is not None and abs(current_step) != 1:
                segment = f"{segment}:{abs(current_step)}"
            out.append(segment)
            expected_position = position + len(run_names)
            index = lookahead
        else:
            out.append(names[0])
            expected_position = position + 1
            index += 1

    return ",".join(out)


def get_stats(code: str) -> StatsData:
    rows = parse_code(code)
    names = [row.name for row in rows]
    positions = {row.position for row in rows}
    types = {_code_type(name) for name in names}
    code_type: CodeType = "mixed" if len(types) != 1 else types.pop()

    all_chars = "".join(names)
    if all_chars:
        frequencies = Counter(all_chars)
        entropy = -sum(
            (count / len(all_chars)) * log2(count / len(all_chars))
            for count in frequencies.values()
        )
    else:
        entropy = 0.0

    return {
        "code_type": code_type,
        "total_rows": len(rows),
        "unique_row_count": len(set(names)),
        "unique_position_count": len(positions),
        "unique_names": set(names),
        "name_entropy": entropy,
        "segment_count": len(
            [segment for segment in code.split(",") if segment.strip()]
        ),
    }


def build_venue(sections: Sequence[SectionInput], venue_name: str) -> VenueOut:
    expanded = [
        SectionOut(name=section.name, rows=parse_code(section.code))
        for section in sections
    ]
    return VenueOut(venue_name=venue_name, sections=expanded)


def venue_diff(a: Venue, b: Venue) -> VenueDiff:
    diff: VenueDiff = {}

    for section_name in sorted(set(a.sections) | set(b.sections)):
        rows_a = (
            {row.name: row.position for row in parse_code(a.sections[section_name])}
            if section_name in a.sections
            else {}
        )
        rows_b = (
            {row.name: row.position for row in parse_code(b.sections[section_name])}
            if section_name in b.sections
            else {}
        )

        section_delta: dict[str, RowPositionDelta] = {}
        for row_name in sorted(set(rows_a) | set(rows_b)):
            if rows_a.get(row_name) != rows_b.get(row_name):
                section_delta[row_name] = {
                    "a": rows_a.get(row_name),
                    "b": rows_b.get(row_name),
                }

        if section_delta:
            diff[section_name] = section_delta

    return diff


__all__ = [
    "parse_code",
    "parse_bulk",
    "compress_rows",
    "get_stats",
    "build_venue",
    "venue_diff",
]
