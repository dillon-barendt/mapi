"""🌐 api.py – FastAPI router for Row‑Progression & Venue operations"""

from __future__ import annotations
from app.schemas.parse import ParsingRequest
from fastapi import APIRouter, HTTPException
from app.schemas import (
    validators as v,
    RowProgression,
    BulkParseResp,
    BulkParsingRequest,
    CodeResp,
    StatsResp,
    VenueOut,
    VenueDiffReq,
    VenueRequest,
)

router = APIRouter()


@router.post("/parse", response_model=RowProgression)
async def parse_code(req: ParsingRequest):
    """
    Handles POST requests to parse a given code and return the progression of
    rows as a response.

    Summary:
        This function is an endpoint for parsing code provided in a request
        object of type `ParsingRequest`. It uses the `parse_code` function to
        process the provided code and generates a progression of rows. If the
        parsing fails with a `ValueError`, an HTTP exception with status code
        400 is raised along with the error details.

    :param req: The request body containing the code to be parsed.
    :type req: ParsingRequest

    :return: A response object containing the originally provided code
        and the parsed progression of rows.
    :rtype: RowProgression

    :raises HTTPException: If the input code cannot be parsed due to a
        `ValueError`.
    """
    try:
        rows = v.parse_code(req.code)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return RowProgression(code=req.code, rows=rows)


@router.post("/bulk-parse", response_model=BulkParseResp)
async def bulk_parse(req: BulkParsingRequest):
    """
    Handles bulk parsing of codes provided in a request payload.

    Accepts a `BulkParsingRequest` object containing a list of codes to be parsed.
    Attempts to process these codes in bulk and returns the parsed results.
    If any error occurs during parsing, an HTTP exception is raised with a 400
    status code and a detailed error message.

    :param req: The BulkParsingRequest object containing the list of codes to be
        parsed.
    :type req: BulkParsingRequest
    :return: A BulkParseResp object containing the parsed results.
    :rtype: BulkParseResp
    :raises HTTPException: If a ValueError occurs during parsing, raised with
        status code 400 and error details.
    """
    try:
        results = v.parse_bulk(req.codes)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return BulkParseResp(results=results)


@router.post("/compress", response_model=CodeResp)
async def compress_rows(prog: RowProgression):
    """
    Compresses rows based on the given row progression and returns the result.

    This function handles the compression of rows contained in the given
    RowProgression object. It invokes the `compress_rows` method of the
    underlying `v` object and wraps the result into a `CodeResp` response.

    :param prog: Object containing the row data and progression details
        required for the compression process.
    :type prog: RowProgression
    :return: Encapsulated result of the row compression.
    :rtype: CodeResp
    """
    return CodeResp(code=v.compress_rows(prog.rows))


@router.post("/stats", response_model=StatsResp)
async def stats(req: ParsingRequest):
    """
    Handles the POST request to the "/stats" endpoint for calculating various statistical
    attributes of the provided code input. This function processes the code, calculates
    statistical metrics such as total rows, unique names, code type, entropy, and segment
    count, and returns the response in the format defined by the StatsResp model. If there
    is an issue in processing the provided code input, an HTTPException is raised.

    :param req: The parsing request containing the input code to be analyzed.
    :type req: ParsingRequest
    :return: A response containing the calculated statistical attributes including total
        rows, unique names, code type, name entropy, and segment count.
    :rtype: StatsResp
    :raises HTTPException: If the input code is invalid or the required metrics cannot
        be computed.
    """
    try:
        tot, uniq, typ, ent, segs = v.get_stats(req.code)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return StatsResp(
        total_rows=tot,
        unique_names=uniq,
        code_type=typ,
        name_entropy=ent,
        segment_count=segs,
    )


# ── Venue endpoints ──────────────────────────────────────────────────────────
@router.post("/build-venue", response_model=VenueOut)
def build_venue(req: VenueRequest):
    """
    Handles requests to build a venue using the provided venue details. This endpoint
    receives a venue build request and attempts to construct a venue with the given
    parameters. If the provided data is invalid, an HTTPException is raised.

    :param req: The request payload containing the details required to build the
        venue. It must include the venue name and venue sections.
    :type req: VenueRequest

    :return: The response containing the details of the successfully built venue.
    :rtype: VenueOut
    """
    try:
        return v.build_venue(req.sections, req.venue_name)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.post("/venue-diff")
def venue_diff(body: VenueDiffReq):
    """
    Handles the HTTP POST request for calculating venue differences.

    This function is tied to the '/venue-diff' endpoint. It receives a request
    body containing two sets of venue data. Using this data, it computes the
    differences between the two and returns the result in the response payload.

    :param body: An instance of `VenueDiffReq` containing venue data to compare.
    :return: A dictionary containing the computed venue differences.
    :rtype: dict
    """
    return {"venue_diff": v.venue_diff(body.a, body.b)}
