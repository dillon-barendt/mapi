from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import StrictStr

from .row import RowProgression


class ParsingRequest(BaseModel):
    """Single row-progression parse request."""

    code: Annotated[
        StrictStr,
        Field(
            min_length=1,
            description="Compact row progression code to parse.",
            examples=["DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ"],
        ),
    ]

    model_config = ConfigDict(
        title="ParseReq",
        strict=True,
        extra="forbid",
        json_schema_extra={"examples": [{"code": "AA:DD,A:C,1:12,13=13W"}]},
    )


class BulkParsingRequest(BaseModel):
    """List-of-codes parsing request."""

    codes: Annotated[
        list[StrictStr],
        Field(
            min_length=1,
            description="Progression codes to parse independently.",
            examples=[["A:C", "1:4,5!,6:10:2"]],
        ),
    ]

    model_config = ConfigDict(
        title="BulkParseReq",
        strict=True,
        extra="forbid",
        json_schema_extra={"examples": [{"codes": ["A:C", "AA:DD,1=1W"]}]},
    )


class BulkParseResp(BaseModel):
    results: Annotated[
        list[RowProgression],
        Field(min_length=1, description="Parsed row progression results."),
    ]

    model_config = ConfigDict(title="BulkParseResp", strict=True, extra="forbid")
