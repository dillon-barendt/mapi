from __future__ import annotations

"""🛠️ validators.py – Row‑progression logic fully aligned with spec.

Includes:
* `parse_code` – spec‑compliant expansion (atomic / slice / gap / equivalent)
* `parse_bulk` – helper to parse many codes
* `compress_rows` – canonical compression back to code string
* `get_stats` – entropy & metadata
* `build_venue` – expands an entire venue request
* `venue_diff` – structural diff between two compact venues
"""

import logging
import re
from math import log2
from typing import Dict, List, Sequence

from app.schemas.row import RowOut, RowProgression
from app.schemas.section import SectionInput, SectionOut
from app.schemas.venue import Venue, VenueOut


logger = logging.getLogger("row_progression.validators")

LETTER_RE = re.compile(r"^([A-Z])\1*$")  # pure repeated letters e.g. A, AA, BBB
NUMBER_RE = re.compile(r"^\d+$")  # pure digits

# ─────────────────────────────────────────────────────────────────────────────
# Helpers: letter <-> index  (1‑based)
# ─────────────────────────────────────────────────────────────────────────────


def _letters_to_index(code: str) -> int:
    idx = 0
    for ch in code:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx


def _index_to_letters(idx: int, length: int) -> str:
    s: list[str] = []
    while idx:
        idx, rem = divmod(idx - 1, 26)
        s.append(chr(rem + ord("A")))
    txt = "".join(reversed(s))
    return txt.rjust(length, txt[-1])  # pad with last char to keep length


# ─────────────────────────────────────────────────────────────────────────────
# Range expansion (supports ascending/descending + step)
# ─────────────────────────────────────────────────────────────────────────────


def _expand_numeric(start: int, end: int, step: int) -> list[str]:
    direction = 1 if end >= start else -1
    rng = range(start, end + direction, step * direction)
    return [str(i) for i in rng]


def _expand_letters(start: str, end: str, step: int) -> list[str]:
    length = len(start)
    si, ei = _letters_to_index(start), _letters_to_index(end)
    direction = 1 if ei >= si else -1

    if length == 1:  # single‑letter slice is end‑exclusive
        out = []
        current = si
        while current < ei if direction == 1 else current > ei:
            out.append(chr(current - 1 + ord("A")))
            current += step * direction
        return out

    rng = range(si, ei + direction, step * direction)
    return [_index_to_letters(i, length) for i in rng]


def _range_codes(start: str, end: str, step: int) -> list[str]:
    if step <= 0:
        raise ValueError("Step must be positive.")
    if NUMBER_RE.fullmatch(start) and NUMBER_RE.fullmatch(end):
        return _expand_numeric(int(start), int(end), step)
    if (
        LETTER_RE.fullmatch(start)
        and LETTER_RE.fullmatch(end)
        and len(start) == len(end)
    ):
        return _expand_letters(start, end, step)
    raise ValueError(f"Invalid slice '{start}:{end}'. Mixed or unequal types.")


# ─────────────────────────────────────────────────────────────────────────────
# Core parser compliant with spec
# ─────────────────────────────────────────────────────────────────────────────


def parse_code(code: str) -> List[RowOut]:
    pos = 1
    rows: list[RowOut] = []
    for raw_segment in code.split(","):
        segment = raw_segment.strip()
        if not segment:
            continue

        gap = segment.endswith("!")
        if gap:
            segment = segment[:-1]

        # Equivalents
        if "=" in segment:
            names = [n.strip() for n in segment.split("=") if n.strip()]
            if len(names) < 2:
                raise ValueError(f"Malformed equivalent segment '{raw_segment}'.")
            if not gap:
                rows.extend(RowOut(name=n, position=pos) for n in names)
            pos += 1
            continue

        parts = segment.split(":")
        if len(parts) == 1:  # atomic
            if not gap:
                rows.append(RowOut(name=parts[0], position=pos))
            pos += 1
        else:  # slice
            start, end = parts[0], parts[1]
            step = int(parts[2]) if len(parts) == 3 else 1
            for name in _range_codes(start, end, step):
                if not gap:
                    rows.append(RowOut(name=name, position=pos))
                pos += 1

    # Uniqueness check
    names = [r.name for r in rows]
    if len(names) != len(set(names)):
        dup = {n for n in names if names.count(n) > 1}
        raise ValueError(f"Duplicate row names: {', '.join(sorted(dup))}")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Bulk helper
# ─────────────────────────────────────────────────────────────────────────────


def parse_bulk(codes: Sequence[str]) -> List[RowProgression]:
    return [RowProgression(code=c, rows=parse_code(c)) for c in codes]


# ─────────────────────────────────────────────────────────────────────────────
# Compression (simple canonicaliser – same as earlier)
# ─────────────────────────────────────────────────────────────────────────────


def _code_type(name: str) -> str:
    if NUMBER_RE.fullmatch(name):
        return "numeric"
    if LETTER_RE.fullmatch(name):
        return "alphabetic"
    return "mixed"


def compress_rows(rows: Sequence[RowOut]) -> str:
    if not rows:
        return ""
    tmp = sorted(rows, key=lambda r: r.position)
    out: list[str] = []
    i = 0

    def same_type(a: str, b: str):
        return _code_type(a) == _code_type(b)

    while i < len(tmp):
        cur, pos = tmp[i].name, tmp[i].position
        # equivalents
        equiv = [cur]
        while i + 1 < len(tmp) and tmp[i + 1].position == pos:
            equiv.append(tmp[i + 1].name)
            i += 1
        if len(equiv) > 1:
            out.append("=".join(equiv))
            i += 1
        else:
            # slice detection
            j, step = i, None
            while j + 1 < len(tmp) and same_type(tmp[j].name, tmp[j + 1].name):
                diff = tmp[j + 1].position - tmp[j].position
                step = diff if step is None else step
                if diff != step:
                    break
                j += 1
            if j > i:
                seg = f"{tmp[i].name}:{tmp[j].name}"
                if step not in (1, None):
                    seg += f":{step}"
                out.append(seg)
                pos = tmp[j].position
                i = j + 1
            else:
                out.append(cur)
                i += 1
        # gap detection
        if i < len(tmp):
            jump = tmp[i].position - pos - 1
            if jump > 0:
                out.append(f"{pos + 1}!")
    return ",".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Stats helper
# ─────────────────────────────────────────────────────────────────────────────


def get_stats(code: str):
    rows = parse_code(code)
    total = len(rows)
    types = {(_code_type(r.name)) for r in rows}
    code_type = "mixed" if len(types) > 1 else types.pop()
    all_chars = "".join(r.name for r in rows)
    freq = {c: all_chars.count(c) for c in set(all_chars)}
    entropy = -sum(
        (cnt / len(all_chars)) * log2(cnt / len(all_chars)) for cnt in freq.values()
    )
    seg_count = len([s for s in code.split(",") if s.strip()])
    return total, total, code_type, entropy, seg_count


# ─────────────────────────────────────────────────────────────────────────────
# Venue helpers
# ─────────────────────────────────────────────────────────────────────────────


def build_venue(sections: Sequence[SectionInput], venue_name: str) -> VenueOut:
    expanded: List[SectionOut] = []
    for sec in sections:
        rows = parse_code(sec.code)
        expanded.append(SectionOut(name=sec.name, rows=rows))
    total = sum(sec.row_count for sec in expanded)
    return VenueOut(venue_name=venue_name, sections=expanded, total_rows=total)


def venue_diff(a: Venue, b: Venue):
    diff: Dict[str, Dict[str, Dict[str, int | None]]] = {}
    all_sec_names = set(a.sections) | set(b.sections)
    for sec in all_sec_names:
        rows_a = (
            {r.name: r.position for r in parse_code(a.sections[sec])}
            if sec in a.sections
            else {}
        )
        rows_b = (
            {r.name: r.position for r in parse_code(b.sections[sec])}
            if sec in b.sections
            else {}
        )
        row_names = set(rows_a) | set(rows_b)
        delta = {
            rn: {"a": rows_a.get(rn), "b": rows_b.get(rn)}
            for rn in row_names
            if rows_a.get(rn) != rows_b.get(rn)
        }
        if delta:
            diff[sec] = delta
    return diff


__all__ = [
    "parse_code",
    "parse_bulk",
    "compress_rows",
    "get_stats",
    "build_venue",
    "venue_diff",
]
