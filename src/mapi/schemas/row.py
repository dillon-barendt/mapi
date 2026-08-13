"""Typed row models returned by the row-progression parser."""

from collections.abc import Sequence
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from pydantic.types import PositiveInt, StrictStr

RowName = Annotated[
    StrictStr,
    Field(
        min_length=1,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$",
        description=(
            "Venue row identifier. Pure ranges use uppercase letters or digits; "
            "mixed rows are atomic."
        ),
        examples=["AA", "12", "12W"],
    ),
]


class RowOut(BaseModel):
    """Immutable row name and 1-based physical position."""

    name: RowName
    position: PositiveInt = Field(
        ...,
        description="1-based row position after accounting for gap rows.",
        examples=[4],
    )

    model_config = ConfigDict(
        title="RowOut",
        strict=True,
        frozen=True,
        json_schema_extra={"examples": [{"name": "AA", "position": 1}]},
    )


class RowProgression(BaseModel):
    """Original compact row code plus expanded rows."""

    code: StrictStr = Field(
        ...,
        min_length=1,
        description="Original compact row progression code string.",
        examples=["AA:DD,A:C,1:12,13=13W"],
    )
    rows: Sequence[RowOut] = Field(
        default_factory=tuple,
        description="Expanded rows. Gap rows are position-only and are not returned.",
    )

    model_config = ConfigDict(
        title="Venue DSL",
        strict=True,
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "code": "AA:CC,1=1W",
                    "rows": [
                        {"name": "AA", "position": 1},
                        {"name": "BB", "position": 2},
                        {"name": "CC", "position": 3},
                        {"name": "1", "position": 4},
                        {"name": "1W", "position": 4},
                    ],
                }
            ]
        },
    )
