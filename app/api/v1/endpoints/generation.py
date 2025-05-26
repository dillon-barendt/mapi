from fastapi import APIRouter

from app.schemas.generation import GenResp, GenReq
from app.services.row_prog import compress_section

router = APIRouter()


@router.post("/generate", response_model=GenResp)
async def generate(req: GenReq):
    """
    Handles the generation of a compressed section of code based on the
    provided input.

    This endpoint receives a request object, processes its rows to compute
    a compressed section of code, and returns the response object.

    :param req: Request object containing the section and rows for processing.
    :type req: GenReq
    :return: Response object containing the generated section, code, and row count.
    :rtype: GenResp
    """
    rows = [(r.name, r.position) for r in req.rows]
    code = compress_section(rows)
    return GenResp(section=req.section, code=code, row_count=len(rows))
