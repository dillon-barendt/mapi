from fastapi import HTTPException, APIRouter

from app.schemas.venue import VenueDiffReq, VenueOut, VenueRequest, SectionOut, RowOut
from app.services.row_prog import parse_row_progression

router = APIRouter()

@router.post("/venue-diff")
async def venue_diff(req: VenueDiffReq):
    """
    Compares the section progression differences between two venues and returns
    a diff containing mismatched rows.

    :param req: The request object containing two venues `a` and `b` which include
        their respective section progression data.
    :type req: VenueDiffReq
    :return: A dictionary containing the differences in sections and mismatched row
        progressions between the two venues.
    :rtype: dict
    """
    diff = {}
    for sec in set(req.a.sections) | set(req.b.sections):
        code_a = req.a.sections.get(sec)
        code_b = req.b.sections.get(sec)
        if code_a == code_b:
            continue
        rows_a = dict(parse_row_progression(code_a)) if code_a else {}
        rows_b = dict(parse_row_progression(code_b)) if code_b else {}
        mismatched = {
            r: {"a": rows_a.get(r), "b": rows_b.get(r)}
            for r in set(rows_a) | set(rows_b)
            if rows_a.get(r) != rows_b.get(r)
        }
        diff[sec] = mismatched
    return {"venue_diff": diff}

# ---------- Endpoint ----------
@router.post("/build‑venue", response_model=VenueOut)
async def build_venue(body: VenueRequest):
    """
    Build venue data based on the provided request body. Parses and processes the given
    sections to calculate row progression and returns the resultant venue details, including
    all processed sections, rows, and the total number of rows.

    :param body: The request body containing the venue and section details
    :type body: VenueRequest
    :return: The processed venue data including venue name, sections with rows, and total row count
    :rtype: VenueOut
    :raises HTTPException: If row progression parsing fails for any section in the request body
    """
    sections_out: list[SectionOut] = []
    total_rows = 0

    for sec in body.sections:
        try:
            rows = parse_row_progression(sec.code)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Section {sec.name}: {e}")

        total_rows += len(rows)
        sections_out.append(
            SectionOut(
                name=sec.name, rows=[RowOut(name=r, position=p) for r, p in rows]
            )
        )

    return VenueOut(
        venue_name=body.venue_name, sections=sections_out, total_rows=total_rows
    )