from fastapi import HTTPException, APIRouter

from app.schemas.venue import VenueDiffReq, VenueOut, VenueRequest, SectionOut, RowOut
from app.services.row_prog import parse_row_progression

router = APIRouter()


@router.post("/venue-diff")
async def venue_diff(req: VenueDiffReq):
    """
    Compares two sets of venue sections and provides the differences for each row in
    those sections.

    The endpoint processes two venue configurations (`a` and `b`) from the request
    and identifies mismatches within the sections and their associated rows. Each
    row within a section is analyzed to determine whether it differs between the
    two configurations. The output is structured as a mapping of sections, each
    containing detailed mismatches between the two inputs.

    :param req: The request payload containing two venue objects (`a` and `b`) with
        sections to be compared.
    :type req: VenueDiffReq

    :return: A dictionary containing the calculated "venue_diff" that represents
        mismatched sections and their rows between the two venue configurations.
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
    Handles the creation of a venue based on a given request body. Parses sections included
    in the request to identify rows and their positions, and compiles the data into a
    structured response. If an error occurs while parsing a section, an HTTP 400 exception
    is raised with details about the specific error.

    :param body: The venue creation request containing venue name and sections.
                 Each section includes a name and a code representing its row
                 progression.
    :type body: VenueRequest

    :return: Structured response including venue name, parsed sections with row
             information, and the total count of rows.
    :rtype: VenueOut
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
