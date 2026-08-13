"""Systematic coverage of the row progression formal grammar.

Each production rule of the context-free grammar gets its own test group:

1. C -> C,C          segment chaining
2. C -> S / C -> S!  slices and gap slices
3. S -> A            atomic codes (pure and mixed)
4. S -> A=A          equivalent rows
5. S -> N:N(:j)      numeric slices
6. S -> Lk:Lk(:j)    repeated-letter slices for every family k = 1..4

Beyond parsing, the suite locks in the two directional invariants:

- round trip:  parse(compress(parse(code))) == parse(code)
- idempotency: compress(parse(compress(rows))) == compress(rows)
"""

import pytest

from mapi.schemas.row import RowOut
from mapi.schemas.section import SectionInput
from mapi.schemas.validators import (
    build_venue,
    compress_rows,
    get_stats,
    parse_bulk,
    parse_code,
)

REFERENCE_CODE = "DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ"


def row_pairs(code: str) -> list[tuple[str, int]]:
    return [(row.name, row.position) for row in parse_code(code)]


def test_reference_example_parses_to_exact_rows() -> None:
    assert parse_code(REFERENCE_CODE) == [
        RowOut(name="DD", position=1),
        RowOut(name="CC", position=2),
        RowOut(name="BB", position=3),
        RowOut(name="AA", position=4),
        RowOut(name="A", position=5),
        RowOut(name="B", position=6),
        RowOut(name="C", position=7),
        RowOut(name="1", position=8),
        RowOut(name="2", position=9),
        RowOut(name="3", position=10),
        RowOut(name="4", position=11),
        RowOut(name="6", position=13),
        RowOut(name="8", position=14),
        RowOut(name="10", position=15),
        RowOut(name="12", position=16),
        RowOut(name="12W", position=16),
        RowOut(name="ZZZ", position=17),
    ]


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("A,B,C", [("A", 1), ("B", 2), ("C", 3)]),
        ("1,A,1W", [("1", 1), ("A", 2), ("1W", 3)]),
        ("A:C,1:3", [("A", 1), ("B", 2), ("C", 3), ("1", 4), ("2", 5), ("3", 6)]),
        (
            "1:2,A:B,AA:BB",
            [("1", 1), ("2", 2), ("A", 3), ("B", 4), ("AA", 5), ("BB", 6)],
        ),
    ],
)
def test_chaining_segments(code: str, expected: list[tuple[str, int]]) -> None:
    assert row_pairs(code) == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("A!,B", [("B", 2)]),
        ("A:C!,D", [("D", 4)]),
        ("A,B:D!,E", [("A", 1), ("E", 5)]),
        ("A:C!,D:F!,G", [("G", 7)]),
        ("A,B!,C!,D", [("A", 1), ("D", 4)]),
        ("1:3:2!,A", [("A", 3)]),
        ("A=B!,C", [("C", 2)]),
    ],
)
def test_gap_slices_advance_position_without_rows(
    code: str, expected: list[tuple[str, int]]
) -> None:
    assert row_pairs(code) == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("1=1W", [("1", 1), ("1W", 1)]),
        ("A=AW", [("A", 1), ("AW", 1)]),
        (
            "1:3,4=4A=4B",
            [("1", 1), ("2", 2), ("3", 3), ("4", 4), ("4A", 4), ("4B", 4)],
        ),
        ("1=1W,2=2A", [("1", 1), ("1W", 1), ("2", 2), ("2A", 2)]),
        ("A!,2=2W", [("2", 2), ("2W", 2)]),
    ],
)
def test_equivalent_rows_share_a_position(
    code: str, expected: list[tuple[str, int]]
) -> None:
    assert row_pairs(code) == expected


@pytest.mark.parametrize(
    ("code", "expected_names"),
    [
        ("1:4", ["1", "2", "3", "4"]),
        ("4:1", ["4", "3", "2", "1"]),
        ("3:3", ["3"]),
        ("1:9:2", ["1", "3", "5", "7", "9"]),
        ("9:1:2", ["9", "7", "5", "3", "1"]),
        ("1:7:3", ["1", "4", "7"]),
        ("7:1:3", ["7", "4", "1"]),
        ("10:100:10", [str(n) for n in range(10, 101, 10)]),
    ],
)
def test_numeric_slices(code: str, expected_names: list[str]) -> None:
    assert [name for name, _ in row_pairs(code)] == expected_names


@pytest.mark.parametrize(
    ("code", "expected_names"),
    [
        ("A:E", ["A", "B", "C", "D", "E"]),
        ("E:A", ["E", "D", "C", "B", "A"]),
        ("A:E:2", ["A", "C", "E"]),
        ("E:A:2", ["E", "C", "A"]),
        ("A:A", ["A"]),
        ("AA:EE", ["AA", "BB", "CC", "DD", "EE"]),
        ("EE:AA", ["EE", "DD", "CC", "BB", "AA"]),
        ("AA:EE:2", ["AA", "CC", "EE"]),
        ("EE:AA:2", ["EE", "CC", "AA"]),
        ("AAA:EEE", ["AAA", "BBB", "CCC", "DDD", "EEE"]),
        ("EEE:AAA", ["EEE", "DDD", "CCC", "BBB", "AAA"]),
        ("AAA:EEE:2", ["AAA", "CCC", "EEE"]),
        ("EEE:AAA:2", ["EEE", "CCC", "AAA"]),
        ("AAAA:EEEE", ["AAAA", "BBBB", "CCCC", "DDDD", "EEEE"]),
        ("EEEE:AAAA", ["EEEE", "DDDD", "CCCC", "BBBB", "AAAA"]),
        ("AAAA:EEEE:2", ["AAAA", "CCCC", "EEEE"]),
        ("EEEE:AAAA:2", ["EEEE", "CCCC", "AAAA"]),
    ],
)
def test_letter_slices_across_all_families(
    code: str, expected_names: list[str]
) -> None:
    assert [name for name, _ in row_pairs(code)] == expected_names


@pytest.mark.parametrize(
    ("code", "expected_names"),
    [
        ("21WC", ["21WC"]),
        ("A1", ["A1"]),
        ("B10,C20", ["B10", "C20"]),
        ("ROW-A,ROW-B", ["ROW-A", "ROW-B"]),
        ("R_1,R_2", ["R_1", "R_2"]),
        ("01", ["01"]),
    ],
)
def test_mixed_atomic_codes(code: str, expected_names: list[str]) -> None:
    assert [name for name, _ in row_pairs(code)] == expected_names


@pytest.mark.parametrize(
    "code",
    [
        "1:4",
        "A:D",
        "AA:DD",
        "HHH:DDD",
        "A,B!,C:D",
        "A,B:C!,D",
        "1:3,4=4W,5:7",
        "A:F:2",
        "9:1:2",
        "EEEE:AAAA:2",
        REFERENCE_CODE,
        "1:10:3,A:F:2,AA!,BB:DD",
    ],
)
def test_parse_compress_parse_round_trip(code: str) -> None:
    rows = parse_code(code)
    canonical = compress_rows(rows)

    assert parse_code(canonical) == rows


@pytest.mark.parametrize("code", ["1:4", "A:D", "1:9:2", REFERENCE_CODE])
def test_compress_is_idempotent(code: str) -> None:
    first = compress_rows(parse_code(code))
    second = compress_rows(parse_code(first))

    assert first == second


def test_compress_single_element_range_emits_atom() -> None:
    assert compress_rows(parse_code("3:3")) == "3"


def test_compress_merges_adjacent_ranges_of_one_family() -> None:
    assert compress_rows(parse_code("A:C,D:F")) == "A:F"


def test_compress_stepped_range_keeps_explicit_step() -> None:
    assert compress_rows(parse_code("1:9:2")) == "1:9:2"
    assert compress_rows(parse_code("9:1:2")) == "9:1:2"


def test_compress_unit_step_omits_step() -> None:
    assert compress_rows(parse_code("1:5")) == "1:5"


def test_compress_empty_rows_returns_empty_string() -> None:
    assert compress_rows([]) == ""


def test_compress_single_row() -> None:
    assert compress_rows([RowOut(name="A", position=1)]) == "A"


def test_compress_sorts_rows_by_position() -> None:
    rows = [
        RowOut(name="C", position=3),
        RowOut(name="A", position=1),
        RowOut(name="B", position=2),
    ]

    assert compress_rows(rows) == "A:C"


def test_compress_encodes_gaps_by_position_not_original_name() -> None:
    rows = parse_code("5!,A")

    canonical = compress_rows(rows)

    assert canonical == "1!,A"
    assert parse_code(canonical) == rows


def test_parse_bulk_pairs_each_code_with_its_rows() -> None:
    result = parse_bulk(["1:3", "A:C"])

    assert len(result) == 2
    assert result[0].code == "1:3"
    assert [row.name for row in result[0].rows] == ["1", "2", "3"]
    assert result[1].code == "A:C"
    assert [row.name for row in result[1].rows] == ["A", "B", "C"]


def test_parse_bulk_empty_sequence() -> None:
    assert parse_bulk([]) == []


def test_parse_bulk_propagates_parse_errors() -> None:
    with pytest.raises(ValueError, match="repeated-letter length"):
        parse_bulk(["1:3", "A:AA"])


def test_build_venue_expands_all_sections() -> None:
    venue = build_venue(
        [
            SectionInput(name="101", code="1:3"),
            SectionInput(name="102", code="A:C"),
        ],
        venue_name="Test Venue",
    )

    assert venue.venue_name == "Test Venue"
    sections = {section.name: section for section in venue.sections}
    assert [row.name for row in sections["101"].rows] == ["1", "2", "3"]
    assert [row.name for row in sections["102"].rows] == ["A", "B", "C"]


@pytest.mark.parametrize(
    ("code", "expected_type"),
    [
        ("1:5", "numeric"),
        ("A:E", "alphabetic"),
        ("AA:EE", "alphabetic"),
        ("1:3,A:C", "mixed"),
        ("1=1W", "mixed"),
    ],
)
def test_stats_code_type(code: str, expected_type: str) -> None:
    assert get_stats(code)["code_type"] == expected_type


def test_stats_entropy_grows_with_name_variety() -> None:
    simple = get_stats("1:3")["name_entropy"]
    varied = get_stats("1:3,A:C,1W,2W,3W")["name_entropy"]

    assert simple > 0.0
    assert varied > simple


@pytest.mark.parametrize(
    ("code", "match"),
    [
        ("A:BB", "repeated-letter length"),
        ("AA:AAA", "repeated-letter length"),
        ("1:A", "Ranges require matching"),
        ("A1:B1", "Ranges require matching"),
        ("A:B:0", "Step must be positive"),
        ("A:B:-1", "Invalid positive step"),
        ("A:B:1.5", "Invalid positive step"),
        ("!,A", "missing a row code"),
        ("A=B:C", "must contain atomic row codes"),
    ],
)
def test_grammar_violations_are_rejected(code: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        parse_code(code)
