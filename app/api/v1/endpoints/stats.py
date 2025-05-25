from fastapi import APIRouter

from app.services.row_prog import parse_row_progression

router = APIRouter()


@router.get("/stats")
async def stats(code: str):
    """
    Provides the extracted statistical data from a specific encoded 'code' string. The
    function analyzes the code to compute the total rows, counts of gaps, equivalent
    segments, and slices present in the given input.

    :param code: The encoded string input to be analyzed.
    :type code: str

    :return: A dictionary containing:
        - "row_count" (int): The total count of parsed rows from the input code.
        - "slice_segments" (int): The number of slice segments present in the input.
        - "gap_segments" (int): The count of gaps '!' in the input code.
        - "equivalent_segments" (int): The count of equivalent segments '=' in the input.
    :rtype: dict
    """
    rows = parse_row_progression(code)
    gap_count = code.count("!")
    equiv_count = code.count("=")
    slice_count = sum(1 for seg in code.split(",") if ":" in seg)
    return {
        "row_count": len(rows),
        "slice_segments": slice_count,
        "gap_segments": gap_count,
        "equivalent_segments": equiv_count,
    }
