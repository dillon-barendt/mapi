# tests/test_roundtrip.py
from hypothesis import given, strategies as st
from app.services.row_prog import parse_row_progression, compress_section

simple_code = st.one_of(
    st.text("ABCDEF", min_size=1, max_size=4),                 # letters
    st.text(st.characters(min_codepoint=48, max_codepoint=57), min_size=1, max_size=3)  # nums
)

@given(st.lists(simple_code, min_size=5, max_size=20))
def test_round_trip(codes):
    rows = [(name, i+1) for i, name in enumerate(codes)]
    compressed = compress_section(rows)
    rows2 = parse_row_progression(compressed)
    assert rows == rows2