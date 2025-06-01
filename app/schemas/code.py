from typing import Annotated, Literal, Set

from pydantic import BaseModel, Field, ConfigDict
from pydantic.types import (
    StrictStr,
    NonNegativeInt,
    PositiveFloat,
)


class CodeResp(BaseModel):
    """Wrapper for compressed code."""

    code: Annotated[StrictStr, Field(..., description="Compressed code string")]

    model_config = ConfigDict(title="CodeResp", strict=True, extra="forbid")


class StatsResp(BaseModel):
    """Row‑progression statistics result."""

    code_type: Literal["numeric", "alphabetic", "mixed"]
    total_rows: Annotated[
        NonNegativeInt,
        Field(..., description="Total number of rows in the progression"),
    ]
    unique_names: Annotated[
        Set[StrictStr],
        Field(..., description="List of unique row names in the progression"),
    ]
    name_entropy: Annotated[
        PositiveFloat, Field(..., description="Entropy of row names in the progression")
    ]
    segment_count: Annotated[
        NonNegativeInt, Field(..., description="Number of segments in the progression")
    ]

    model_config = ConfigDict(title="StatsResp", strict=True)
