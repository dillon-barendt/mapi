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
    """Expand **one** code into concrete rows."""
    try:
        rows = v.parse_code(req.code)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return RowProgression(code=req.code, rows=rows)


@router.post("/bulk-parse", response_model=BulkParseResp)
async def bulk_parse(req: BulkParsingRequest):
    """Expand **many** codes in one request."""
    try:
        results = v.parse_bulk(req.codes)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return BulkParseResp(results=results)


@router.post("/compress", response_model=CodeResp)
async def compress_rows(prog: RowProgression):
    """Turn a list of rows back into a compact code string."""
    return CodeResp(code=v.compress_rows(prog.rows))


@router.post("/stats", response_model=StatsResp)
async def stats(req: ParsingRequest):
    """Return row‑count, entropy, etc. for a code."""
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
    """Expand a whole venue (all sections)."""
    try:
        return v.build_venue(req.sections, req.venue_name)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.post("/venue-diff")
def venue_diff(body: VenueDiffReq):
    """Diff two compact venue snapshots."""
    return {"venue_diff": v.venue_diff(body.a, body.b)}
