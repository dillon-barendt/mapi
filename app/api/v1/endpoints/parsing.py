from fastapi import APIRouter
from fastapi import HTTPException, Query

from app.schemas import BulkResp, BulkReq, ParseReq
from app.services.row_prog import parse_row_progression

router = APIRouter()


@router.post("/parse")
async def parse_endpoint(body: ParseReq):
    """
    Handles the parsing of code to extract and structure row progression details.

    This endpoint receives a request body containing code, processes it to generate
    row progression data, and returns a structured response. If the parsing fails
    due to invalid input, an HTTPException with a 400 status code is raised.

    :param body: The request payload containing the input code to be processed.
    :type body: ParseReq
    :return: A dictionary containing parsed row progression data where each item
             includes a name and position.
    :rtype: dict
    :raises HTTPException: If the input code cannot be parsed or is invalid.
    """
    try:
        rows = parse_row_progression(body.code)
        return {"rows": [{"name": n, "position": p} for n, p in rows]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-parse", response_model=BulkResp)
async def bulk_parse(req: BulkReq):
    """
    Handles the bulk parsing of codes and provides a structured response with parsed results or error
    messages if exceptions occur during the parsing process. The API endpoint processes an array of
    codes and attempts to parse each code using the `parse_row_progression` function. If parsing fails
    for any code, the error message is included in the response.

    :param req: Incoming request containing a list of codes to be parsed.
    :type req: BulkReq
    :return: Response containing a dictionary of codes mapped to their parsed results or error
             messages if exceptions occur.
    :rtype: BulkResp
    """
    out = {}
    for c in req.codes:
        try:
            from app.services.row_prog import parse_row_progression

            out[c] = parse_row_progression(c)
        except Exception as e:
            out[c] = {"error": str(e)}
    return {"parsed": out}


@router.get("/validate")
async def validate_endpoint(code: str = Query(..., description="Row‑progression code")):
    """
    Handles the validation of a row-progression code, ensuring that the provided code
    complies with the expected format and standards. The endpoint leverages the
    `parse_row_progression` function to perform the validation. If the code is invalid,
    the endpoint captures the exception and provides an error response.

    :param code: The row-progression code provided as input for validation.
    :type code: str
    :return: A dictionary containing the validation result. If valid, the dictionary contains
        "valid" set to True. If invalid, the dictionary includes "valid" set to False and
        an "error" message describing the issue.
    :rtype: dict
    """
    try:
        parse_row_progression(code)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}
