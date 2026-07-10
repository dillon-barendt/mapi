from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import NonNegativeFloat, NonNegativeInt, StrictStr


class CodeResp(BaseModel):
    """Wrapper for compressed row progression code."""

    code: Annotated[
        StrictStr,
        Field(
            description="Canonical compact row progression code.",
            examples=["AA:CC,1=1W"],
        ),
    ]

    model_config = ConfigDict(title="CodeResp", strict=True, extra="forbid")


class StatsResp(BaseModel):
    """Row-progression statistics result."""

    code_type: Literal["numeric", "alphabetic", "mixed"] = Field(
        ...,
        description=(
            "Dominant code family. Mixed means multiple families or no returned rows."
        ),
        examples=["mixed"],
    )
    total_rows: NonNegativeInt = Field(
        ...,
        description="Number of returned row names, including equivalent aliases.",
        examples=[5],
    )
    unique_row_count: NonNegativeInt = Field(
        ...,
        description="Number of unique returned row names.",
        examples=[5],
    )
    unique_position_count: NonNegativeInt = Field(
        ...,
        description="Number of physical row positions represented by returned rows.",
        examples=[4],
    )
    unique_names: set[StrictStr] = Field(
        ...,
        description="Unique returned row names.",
        examples=[["AA", "BB", "CC", "1", "1W"]],
    )
    name_entropy: NonNegativeFloat = Field(
        ...,
        description="Shannon entropy across characters in returned row names.",
        examples=[2.16],
    )
    segment_count: NonNegativeInt = Field(
        ...,
        description="Number of comma-delimited DSL segments in the submitted code.",
        examples=[2],
    )

    model_config = ConfigDict(
        title="StatsResp",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "code_type": "mixed",
                    "total_rows": 5,
                    "unique_row_count": 5,
                    "unique_position_count": 4,
                    "unique_names": ["1", "1W", "AA", "BB", "CC"],
                    "name_entropy": 2.16,
                    "segment_count": 2,
                }
            ]
        },
    )
