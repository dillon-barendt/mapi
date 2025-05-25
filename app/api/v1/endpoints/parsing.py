from fastapi import APIRouter
from fastapi import HTTPException, Query

from app.schemas import BulkResp, BulkReq, ParseReq
from app.services.row_prog import parse_row_progression

router = APIRouter()

@router.post("/parse")
async def parse_endpoint(body: ParseReq):
    """
    Handles HTTP POST requests to parse a provided body containing code and computes
    row progression data. Returns a structured representation of the parsed rows.

    :param body: The input request body containing the code to be parsed.
    :type body: ParseReq
    :return: A dictionary containing the parsed rows with their corresponding name
             and position.
    :rtype: dict
    :raises HTTPException: If the provided code is invalid, raises an HTTP 400
                           exception with an error detail message.
    """
    try:
        rows = parse_row_progression(body.code)
        return {"rows": [{"name": n, "position": p} for n, p in rows]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-parse", response_model=BulkResp)
async def bulk_parse(req: BulkReq):
    """
    Handles bulk parsing of progression codes provided in the request and returns
    the parsed data. For each code in the request, attempts to parse the data
    and collects the result. If any errors occur during parsing, they are captured
    and included in the response.

    :param req: BulkReq instance containing the list of progression codes to parse.
    :type req: BulkReq
    :return: A dictionary with parsed data for each code. If an error occurs during
        parsing of a specific code, the error message is included in the result
        corresponding to the code.
    :rtype: dict
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
    Validates a given row-progression code by attempting to parse it. If the parsing
    is successful, it returns a response indicating validity. If parsing fails, it
    returns a response with the error details.

    :param code: The row-progression code to validate.
    :type code: str
    :return: A dictionary indicating whether the code is valid and, if invalid,
             includes error details.
    :rtype: dict
    """
    try:
        parse_row_progression(code)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}
