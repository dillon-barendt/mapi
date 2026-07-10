from __future__ import annotations

import csv
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from mapi.schemas.row import RowOut
from mapi.schemas.validators import compress_rows


@dataclass(frozen=True, slots=True)
class SpreadsheetRowRecord:
    section: str
    row: str
    position: int


def _clean_record(
    *,
    section: str | None,
    row: str | None,
    position: str | int | None,
    source: str,
) -> SpreadsheetRowRecord:
    clean_section = (section or "").strip()
    clean_row = (row or "").strip()

    if not clean_section:
        raise ValueError(f"{source}: section must be non-empty.")
    if not clean_row:
        raise ValueError(f"{source}: row must be non-empty.")

    try:
        clean_position = int(position) if position is not None else 0
    except (TypeError, ValueError) as error:
        raise ValueError(f"{source}: position must be a positive integer.") from error

    if clean_position <= 0:
        raise ValueError(f"{source}: position must be a positive integer.")

    return SpreadsheetRowRecord(
        section=clean_section,
        row=clean_row,
        position=clean_position,
    )


def normalize_record(record: SpreadsheetRowRecord) -> SpreadsheetRowRecord:
    return _clean_record(
        section=record.section,
        row=record.row,
        position=record.position,
        source=f"section {record.section!r} row {record.row!r}",
    )


def load_csv_records(path: str | Path) -> list[SpreadsheetRowRecord]:
    csv_path = Path(path)
    records: list[SpreadsheetRowRecord] = []

    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required_columns = {"section", "row", "position"}
        fieldnames = set(reader.fieldnames or [])
        missing_columns = sorted(required_columns - fieldnames)
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise ValueError(f"{csv_path}: missing required CSV columns: {missing}.")

        for line_number, row in enumerate(reader, start=2):
            records.append(
                _clean_record(
                    section=row.get("section"),
                    row=row.get("row"),
                    position=row.get("position"),
                    source=f"{csv_path}: line {line_number}",
                )
            )

    return records


def compress_section_rows(records: Sequence[SpreadsheetRowRecord]) -> dict[str, str]:
    grouped_rows: dict[str, list[RowOut]] = defaultdict(list)
    seen_names: dict[str, set[str]] = defaultdict(set)

    for record in records:
        clean_record = normalize_record(record)
        if clean_record.row in seen_names[clean_record.section]:
            raise ValueError(
                "Duplicate row name "
                f"{clean_record.row!r} in section {clean_record.section!r}."
            )
        seen_names[clean_record.section].add(clean_record.row)
        grouped_rows[clean_record.section].append(
            RowOut(name=clean_record.row, position=clean_record.position)
        )

    return {
        section: compress_rows(grouped_rows[section])
        for section in sorted(grouped_rows)
    }
