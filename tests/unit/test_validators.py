import pytest
from hypothesis import given
from hypothesis import strategies as st

from mapi.schemas.row import RowOut
from mapi.schemas.validators import compress_rows, get_stats, parse_code, venue_diff
from mapi.schemas.venue import Venue


def row_pairs(code: str) -> list[tuple[str, int]]:
    return [(row.name, row.position) for row in parse_code(code)]


def test_parses_numeric_ranges_inclusive_descending_and_stepped() -> None:
    assert row_pairs("1:4") == [("1", 1), ("2", 2), ("3", 3), ("4", 4)]
    assert row_pairs("5:1") == [
        ("5", 1),
        ("4", 2),
        ("3", 3),
        ("2", 4),
        ("1", 5),
    ]
    assert row_pairs("5:1:2") == [("5", 1), ("3", 2), ("1", 3)]


def test_parses_letter_ranges_inclusive_descending_and_stepped() -> None:
    assert row_pairs("A:D") == [("A", 1), ("B", 2), ("C", 3), ("D", 4)]
    assert row_pairs("D:A") == [("D", 1), ("C", 2), ("B", 3), ("A", 4)]
    assert row_pairs("A:F:2") == [("A", 1), ("C", 2), ("E", 3)]


def test_parses_multi_letter_ranges_as_repeated_letter_families() -> None:
    assert row_pairs("AA:DD") == [
        ("AA", 1),
        ("BB", 2),
        ("CC", 3),
        ("DD", 4),
    ]
    assert row_pairs("HHH:DDD") == [
        ("HHH", 1),
        ("GGG", 2),
        ("FFF", 3),
        ("EEE", 4),
        ("DDD", 5),
    ]


def test_parses_equivalent_rows_and_gaps() -> None:
    assert row_pairs("A,B:C!,D=DW") == [
        ("A", 1),
        ("D", 4),
        ("DW", 4),
    ]


def test_parses_mixed_rows_as_atoms() -> None:
    assert row_pairs("A1,21WC,B10") == [("A1", 1), ("21WC", 2), ("B10", 3)]


def test_parses_original_complex_example() -> None:
    assert row_pairs("DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ") == [
        ("DD", 1),
        ("CC", 2),
        ("BB", 3),
        ("AA", 4),
        ("A", 5),
        ("B", 6),
        ("C", 7),
        ("1", 8),
        ("2", 9),
        ("3", 10),
        ("4", 11),
        ("6", 13),
        ("8", 14),
        ("10", 15),
        ("12", 16),
        ("12W", 16),
        ("ZZZ", 17),
    ]


@pytest.mark.parametrize(
    "code",
    [
        "",
        "A,,B",
        "A:B:C:D",
        "A:AA",
        "A1:B1",
        "1:A",
        "A:B:0",
        "A:B:-1",
        "A:=B",
        "A:B=C",
        "A!B",
    ],
)
def test_rejects_malformed_codes(code: str) -> None:
    with pytest.raises(ValueError):
        parse_code(code)


@pytest.mark.parametrize("code", ["A,A", "A=B,A", "A=A"])
def test_rejects_duplicate_returned_rows(code: str) -> None:
    with pytest.raises(ValueError, match="Duplicate row"):
        parse_code(code)


def test_compress_round_trips_complex_code() -> None:
    original = "DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ"
    compressed = compress_rows(parse_code(original))

    assert compressed == "DD:AA,A:C,1:4,12!,6:10:2,12=12W,ZZZ"
    assert parse_code(compressed) == parse_code(original)


def test_compress_preserves_leading_and_middle_gaps() -> None:
    rows = [
        RowOut(name="A", position=3),
        RowOut(name="B", position=5),
        RowOut(name="BW", position=5),
    ]

    compressed = compress_rows(rows)

    assert compressed == "1:2!,A,4!,B=BW"
    assert parse_code(compressed) == rows


def test_get_stats_reports_unique_counts() -> None:
    stats = get_stats("AA:CC,1=1W")

    assert stats["total_rows"] == 5
    assert stats["unique_row_count"] == 5
    assert stats["unique_position_count"] == 4
    assert stats["unique_names"] == {"AA", "BB", "CC", "1", "1W"}
    assert stats["segment_count"] == 2


def test_venue_diff_reports_position_changes_and_missing_rows() -> None:
    old = Venue(name="Old", sections={"101": "A:C"})
    new = Venue(name="New", sections={"101": "A:B,D", "102": "1:2"})

    assert venue_diff(old, new) == {
        "101": {"C": {"a": 3, "b": None}, "D": {"a": None, "b": 3}},
        "102": {"1": {"a": None, "b": 1}, "2": {"a": None, "b": 2}},
    }


row_name_strategy = st.one_of(
    st.integers(min_value=1, max_value=300).map(str),
    st.sampled_from(
        [
            "A",
            "B",
            "C",
            "D",
            "AA",
            "BB",
            "CC",
            "DD",
            "AAA",
            "BBB",
            "CCC",
        ]
    ),
    st.from_regex(r"[A-Z][A-Z0-9]{0,2}W?", fullmatch=True),
)


@given(
    st.lists(
        st.tuples(
            st.lists(row_name_strategy, min_size=1, max_size=3, unique=True),
            st.integers(min_value=0, max_value=2),
        ),
        min_size=1,
        max_size=8,
    ).filter(
        lambda groups: (
            len([name for names, _ in groups for name in names])
            == len({name for names, _ in groups for name in names})
        )
    )
)
def test_generated_rows_round_trip_through_compression(
    groups: list[tuple[list[str], int]],
) -> None:
    rows: list[RowOut] = []
    position = 1
    for names, gap_before in groups:
        position += gap_before
        rows.extend(RowOut(name=name, position=position) for name in names)
        position += 1

    compressed = compress_rows(rows)

    assert parse_code(compressed) == rows
