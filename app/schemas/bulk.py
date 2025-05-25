# ─────────────────────  Bulk & slice‑info models  ─────────────────────
from typing import Dict

from pydantic import BaseModel, conlist

from app.schemas.shared import RowCode


class BulkReq(BaseModel):
    """
    Represents a bulk request object designed to handle a list of `RowCode` instances.
    This class validates the provided list to ensure it adheres to defined constraints
    and facilitates structured access to the data.

    The `codes` attribute must contain at least one `RowCode` instance and can accept
    up to a maximum of 10,000 entries. This ensures efficient handling of batch
    processing operations.

    :ivar codes: A list of `RowCode` instances representing the individual items
        in the bulk request. The list must contain at least 1 and at most 10,000 elements.
    :type codes: conlist(RowCode, min_length=1, max_length=10_000)
    """
    codes: conlist(RowCode, min_length=1, max_length=10_000)

    model_config = {"title": "BulkParseRequest", "strict": True, "extra": "forbid"}


class BulkResp(BaseModel):
    """
    Represents the response for bulk parsing operations.

    This class is designed to handle and encapsulate the results of a bulk parsing
    operation. It stores parsed data in a structured format that associates specific
    row codes with corresponding lists of string and integer tuples. The configuration
    for this model enforces a title, frozen instances, and strict validation.

    :ivar parsed: A dictionary mapping `RowCode` to a list of tuples. Each tuple
        consists of a string and an integer, representing parsed data related to the
        respective row code.
    :type parsed: Dict[RowCode, List[Tuple[str, int]]]
    """
    parsed: Dict[RowCode, list[tuple[str, int]]]

    model_config = {"title": "BulkParseResponse", "frozen": True, "strict": True}