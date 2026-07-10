from pathlib import Path

import pytest

from mapi.services.spreadsheet_import import (
    SpreadsheetRowRecord,
    compress_section_rows,
    load_csv_records,
)


def test_compresses_csv_records_grouped_by_section() -> None:
    records = [
        SpreadsheetRowRecord("101", "AA", 1),
        SpreadsheetRowRecord("101", "BB", 2),
        SpreadsheetRowRecord("101", "CC", 3),
        SpreadsheetRowRecord("101", "DD", 4),
        SpreadsheetRowRecord("101", "A", 5),
        SpreadsheetRowRecord("101", "B", 6),
        SpreadsheetRowRecord("101", "C", 7),
        SpreadsheetRowRecord("101", "13", 20),
        SpreadsheetRowRecord("101", "13W", 20),
    ]

    assert compress_section_rows(records) == {"101": "AA:DD,A:C,8:19!,13=13W"}


def test_aliases_and_gaps_are_preserved() -> None:
    records = [
        SpreadsheetRowRecord("101", "A", 1),
        SpreadsheetRowRecord("101", "D", 4),
        SpreadsheetRowRecord("101", "DW", 4),
    ]

    assert compress_section_rows(records) == {"101": "A,2:3!,D=DW"}


@pytest.mark.parametrize(
    "record, message",
    [
        (SpreadsheetRowRecord("101", "A", 0), "position"),
        (SpreadsheetRowRecord("", "A", 1), "section"),
        (SpreadsheetRowRecord("101", "", 1), "row"),
    ],
)
def test_invalid_records_are_rejected(
    record: SpreadsheetRowRecord,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        compress_section_rows([record])


def test_duplicate_row_names_within_section_are_rejected() -> None:
    records = [
        SpreadsheetRowRecord("101", "A", 1),
        SpreadsheetRowRecord("101", "A", 2),
    ]

    with pytest.raises(ValueError, match="Duplicate row name"):
        compress_section_rows(records)


def test_same_row_name_in_different_sections_is_allowed() -> None:
    records = [
        SpreadsheetRowRecord("102", "A", 1),
        SpreadsheetRowRecord("101", "A", 1),
    ]

    assert list(compress_section_rows(records)) == ["101", "102"]
    assert compress_section_rows(records) == {"101": "A", "102": "A"}


def test_load_csv_records_rejects_missing_columns(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("section,row\n101,A\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required CSV columns: position"):
        load_csv_records(path)


def test_load_csv_records_rejects_invalid_rows(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("section,row,position\n101,A,not-a-number\n", encoding="utf-8")

    with pytest.raises(ValueError, match="line 2"):
        load_csv_records(path)


def test_load_csv_records_reads_valid_csv(tmp_path: Path) -> None:
    path = tmp_path / "rows.csv"
    path.write_text("section,row,position\n101,A,1\n101,B,2\n", encoding="utf-8")

    assert load_csv_records(path) == [
        SpreadsheetRowRecord("101", "A", 1),
        SpreadsheetRowRecord("101", "B", 2),
    ]
