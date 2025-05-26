from fastapi import HTTPException, APIRouter

from app.services.row_prog import parse_row_progression

router = APIRouter()


@router.get("/lookup-position")
async def lookup(code: str, name: str):
    """
    Handles lookup of a specific row name and its position within the progression of rows
    derived from a given code. Returns the position of the requested row name if it exists
    within the resulting progression; otherwise, raises a `404 Not Found` error.

    :param code: The input code used to generate the row progression.
    :type code: str
    :param name: The name of the row to look up within the generated progression.
    :type name: str
    :return: A dictionary containing the requested row name and its position.
    :rtype: dict
    :raises HTTPException: If the specified row name is not found within the generated
        progression of rows.
    """
    rows = dict(parse_row_progression(code))
    if name not in rows:
        raise HTTPException(status_code=404, detail=f"Row '{name}' not found in code.")
    return {"row": name, "position": rows[name]}
