from typing import List

from app.schemas import SliceOut, SliceInfoReq
from app.services.row_prog import parse_row_progression
from fastapi import APIRouter

router = APIRouter()

@router.post("/slice-info", response_model=List[SliceOut])
async def slice_info(body: SliceInfoReq) -> List[SliceOut]:
    """
    Handles the processing of slice information based on the input request and
    returns a structured output of slices with additional information.

    This function parses the `code` attribute of the provided
    `SliceInfoReq` object. It splits the input based on commas, processes each
    entry by its content format (e.g., single value, range, or equivalent),
    and creates a list of `SliceOut` objects with details such as type, text,
    start position, and end position. Additionally, entries ending with an
    exclamation mark are marked as gaps.

    :param body: The input request containing the `code` string to be parsed.
                 Expected to follow specific formatting rules for slice
                 descriptions.
    :type body: SliceInfoReq

    :return: A list of `SliceOut` objects detailing the parsed slices, with
             information about their kind (e.g., single, equivalent, slice, gap),
             textual representation, and their start and end positions.
    :rtype: List[SliceOut]
    """
    segs, pos = [], 1
    for raw in body.code.split(","):
        gap = raw.endswith("!")
        text = raw[:-1] if gap else raw

        if "=" in text:
            segs.append(SliceOut(kind="equivalent", text=raw, start=pos, end=pos))
            pos += 1
            continue
        parts = text.split(":")
        if len(parts) == 1:
            segs.append(SliceOut(kind="single", text=raw, start=pos, end=pos))
            pos += 1
        else:
            # quick len calc via parser
            span = len(parse_row_progression(text))
            segs.append(
                SliceOut(
                    kind="gap" if gap else "slice",
                    text=raw,
                    start=pos,
                    end=pos + span - 1,
                )
            )
            pos += span
    return segs