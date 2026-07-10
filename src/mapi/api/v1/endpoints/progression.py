from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from mapi.agents import run_mapi_agent
from mapi.schemas import (
    BulkParseResp,
    BulkParsingRequest,
    CodeResp,
    MapiAgentRequest,
    MapiAgentResp,
    ParseReq,
    RowImportRequest,
    RowImportResponse,
    RowProgression,
    StatsResp,
    VenueDiffReq,
    VenueDiffResp,
    VenueOut,
    VenueRequest,
)
from mapi.schemas import validators as row_progression
from mapi.services import SpreadsheetRowRecord, compress_section_rows

router = APIRouter()


def _bad_request(error: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    )


@router.post(
    "/parse",
    response_model=RowProgression,
    summary="Parse one row progression code",
    description=(
        "Expands a compact DSL such as `AA:DD,A:C,1:12,13=13W` into typed row "
        "objects. Gap rows consume positions but are not returned."
    ),
)
async def parse_code(req: ParseReq) -> RowProgression:
    try:
        rows = row_progression.parse_code(req.code)
    except ValueError as error:
        raise _bad_request(error) from error
    return RowProgression(code=req.code, rows=rows)


@router.post(
    "/bulk-parse",
    response_model=BulkParseResp,
    summary="Parse multiple row progression codes",
    description=(
        "Parses each submitted progression independently and returns typed row lists."
    ),
)
async def bulk_parse(req: BulkParsingRequest) -> BulkParseResp:
    try:
        results = row_progression.parse_bulk(req.codes)
    except ValueError as error:
        raise _bad_request(error) from error
    return BulkParseResp(results=results)


@router.post(
    "/compress",
    response_model=CodeResp,
    summary="Compress expanded rows",
    description=(
        "Builds a canonical progression code from typed rows while preserving row "
        "positions, gaps, and equivalent row aliases."
    ),
)
async def compress_rows(prog: RowProgression) -> CodeResp:
    try:
        code = row_progression.compress_rows(prog.rows)
    except ValueError as error:
        raise _bad_request(error) from error
    return CodeResp(code=code)


@router.post(
    "/stats",
    response_model=StatsResp,
    summary="Summarize one row progression code",
    description=(
        "Returns row counts, unique position counts, code-family classification, "
        "character entropy, and segment counts for a compact progression."
    ),
)
async def stats(req: ParseReq) -> StatsResp:
    try:
        return StatsResp(**row_progression.get_stats(req.code))
    except ValueError as error:
        raise _bad_request(error) from error


@router.post(
    "/build-venue",
    response_model=VenueOut,
    summary="Expand a compact venue definition",
    description=(
        "Parses section-level progression codes and returns a typed venue model with "
        "expanded rows and computed row counts."
    ),
)
def build_venue(req: VenueRequest) -> VenueOut:
    try:
        return row_progression.build_venue(req.sections, req.venue_name)
    except ValueError as error:
        raise _bad_request(error) from error


@router.post(
    "/venue-diff",
    response_model=VenueDiffResp,
    summary="Diff two compact venues",
    description=(
        "Compares two compact venue maps and returns changed row positions keyed by "
        "section and row name."
    ),
)
def venue_diff(body: VenueDiffReq) -> VenueDiffResp:
    try:
        diff = row_progression.venue_diff(body.a, body.b)
    except ValueError as error:
        raise _bad_request(error) from error
    return VenueDiffResp.model_validate({"venue_diff": diff})


@router.post(
    "/import-rows",
    response_model=RowImportResponse,
    summary="Import spreadsheet-shaped rows",
    description=(
        "Converts section,row,position records from spreadsheet-style broker "
        "workflows into compact row progression DSL values."
    ),
)
def import_rows(req: RowImportRequest) -> RowImportResponse:
    try:
        records = [
            SpreadsheetRowRecord(
                section=row.section,
                row=row.row,
                position=row.position,
            )
            for row in req.rows
        ]
        sections = compress_section_rows(records)
    except ValueError as error:
        raise _bad_request(error) from error
    return RowImportResponse(sections=sections)


@router.post(
    "/agent/analyze",
    response_model=MapiAgentResp,
    summary="Analyze a row progression with the Mapi agent",
    description=(
        "Runs the Pydantic AI-backed Mapi agent against a compact section code. "
        "The default local agent requires no external model key and returns "
        "parser-grounded mapping, Redis, and review-workflow guidance."
    ),
)
async def analyze_with_agent(req: MapiAgentRequest) -> MapiAgentResp:
    try:
        return await run_mapi_agent(req)
    except ValueError as error:
        raise _bad_request(error) from error
