import pytest
from app.schemas.row import Row, RowProgression, parse_code_to_rows
from pydantic import ValidationError


class TestRowProgressionValidation:
    def test_parse_code_to_rows_validate_call(self):
        # Valid calls
        rows = parse_code_to_rows("row1, row2")
        assert len(rows) == 2
        assert rows[0].name == "row1"
        assert rows[1].name == "row2"

        # Type checking from @validate_call
        with pytest.raises(ValidationError):
            parse_code_to_rows(123)  # Not a string

        with pytest.raises(ValidationError):
            parse_code_to_rows(None)  # None value

        # Empty validation from BeforeValidator(strip_non_empty)
        with pytest.raises(ValueError):
            parse_code_to_rows("")

        with pytest.raises(ValueError):
            parse_code_to_rows("   ")

        # Duplicate validation inside the function
        with pytest.raises(ValueError) as exc_info:
            parse_code_to_rows("row1, row2, row1")
        assert "Row names must be unique" in str(exc_info.value)

    def test_row_progression_model_validation(self):
        # Basic validation works
        rp = RowProgression(code="row1, row2")
        assert len(rp.rows) == 2
        assert rp.rows[0].name == "row1"

        # Code field validates via BeforeValidator
        with pytest.raises(ValidationError) as exc_info:
            RowProgression(code="")
        assert "Field cannot be empty" in str(exc_info.value)

        # Duplicate rows check in populate_rows
        with pytest.raises(ValidationError) as exc_info:
            RowProgression(code="row1, row2, row1")
        assert "Row names must be unique" in str(exc_info.value)

        # Empty rows check in populate_rows (this would happen if all segments were empty)
        with pytest.raises(ValidationError) as exc_info:
            # This code technically isn't empty, but all segments are empty after splitting
            RowProgression(code=",,,")
        assert "must contain at least one row" in str(exc_info.value)

        # Validation against 10 row progression codes
        valid_codes = [
            "row1", "row1, row2", "rowA, rowB, rowC",
            "test1, test2, test3", "value1",
            "item1, item2", "name1, name2, name3",
            "r1, r2", "a1, b1, c1", "single_row"
        ]
        for code in valid_codes:
            rp = RowProgression(code=code)
            assert len(rp.rows) == len(code.split(","))
            for i, segment in enumerate(code.split(",")):
                assert rp.rows[i].name == segment.strip()