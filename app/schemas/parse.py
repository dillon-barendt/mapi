from typing import Sequence, Annotated, List

from pydantic import BaseModel, Field
from pydantic.types import StrictStr
from pydantic.config import ConfigDict

from .row import RowProgression


class ParsingRequest(BaseModel):
    code: StrictStr
    model_config = ConfigDict(title="ParseReq", strict=True, extra="forbid")


class BulkParsingRequest(BaseModel):
    """List-of-codes parsing request."""

    codes: Annotated[
        List[StrictStr],
        Field(min_length=1, description="List of progression codes to parse"),
    ]
    model_config = ConfigDict(title="BulkParseReq", strict=True, extra="forbid")


class BulkParseResp(BaseModel):
    results: Annotated[
        Sequence[RowProgression],
        Field(min_length=1, description="Sequence of parsed rows"),
    ]

    model_config = ConfigDict(title="BulkParseResp", strict=True, extra="forbid")
