from fastapi import APIRouter

from app.schemas.generation import GenResp, GenReq
from app.services.row_prog import compress_section

router = APIRouter()

@router.post("/generate", response_model=GenResp)
async def generate(req: GenReq):
    """
    Handles the endpoint for generating a response based on the given request.

    This function receives a request payload containing rows of data and a section
    identifier. It processes the rows by extracting relevant details, compresses
    the extracted details using an external utility, and returns a structured
    response with the processed data.

    :param req: The input object containing the section identifier and rows of
        data to be processed.
    :type req: GenReq
    :return: A structured response model containing the section identifier, the
        compressed code, and a count of the rows processed.
    :rtype: GenResp
    """
    rows = [(r.name, r.position) for r in req.rows]
    code = compress_section(rows)
    return GenResp(section=req.section, code=code, row_count=len(rows))
