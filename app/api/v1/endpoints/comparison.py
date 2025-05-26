from fastapi import APIRouter

from app.schemas import CompareReq
from app.services.row_prog import parse_row_progression

router = APIRouter()


@router.post("/compare")
async def compare_endpoint(body: CompareReq):
    """
    This endpoint serves as a QA diff tool to identify discrepancies in the position mapping between
    two input code sources (code_a and code_b). It utilizes the same parsing engine as the `/parse` endpoint
    to interpret the input codes and generate respective {row_name: position} mappings. The comparison is
    performed on these mappings using a diff algorithm, which identifies discrepancies in row positions or
    missing rows between the two sources. Discrepancies are highlighted to assist in preventing inadvertent
    row-order drift during operations.

    Particularly beneficial for SeatGeek-style operational teams, this endpoint can be integrated into
    CI processes to flag issues in row positioning before production deployment. For instance, if a row
    "AA" is unexpectedly shifted from position 1 to 4 in one of the sources, this diff tool detects the
    inconsistency before any data modifications propagate further.

    :param body: The request body containing the input `code_a` and `code_b` to be compared.
                 Encapsulated in a `CompareReq` object.
    :type body: CompareReq
    :return: A JSON object highlighting differences in row positions between `code_a` and `code_b`.
             The differences are structured as `{row_name: {"a": position_in_code_a,
             "b": position_in_code_b}}`.
    :rtype: dict
    """
    """
    This endpoint acts as a QA diff tool. It parses two codes (code_a, code_b) with the same engine as /parse, then converts
    each result into a {row_name: position} map. The diff algorithm runs set union on the keys, flagging any row whose position
    is missing or different between sources. SeatGeek‑style ops teams can drop this into CI to prevent accidental row‑order
    drift: if a partner feed suddenly calls row “AA” position 4 instead of 1, the JSON diff highlights it before the data hits production.
    """
    """
    This endpoint acts as a QA diff tool. It parses two codes (code_a, code_b) with the same engine as /parse,
     then converts each result into a {row_name: position} map. The diff algorithm runs set union on the keys,
     flagging any row whose position is missing or different between sources. SeatGeek‑style ops teams can drop
     this into CI to prevent accidental row‑order drift: if a partner feed suddenly calls row “AA” position 4
     instead of 1, the JSON diff highlights it before the data hits production.
    """
    a = dict(parse_row_progression(body.code_a))
    b = dict(parse_row_progression(body.code_b))
    diff = {
        name: {"a": a.get(name), "b": b.get(name)}
        for name in set(a) | set(b)
        if a.get(name) != b.get(name)
    }
    return {"differences": diff}
