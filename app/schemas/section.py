from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic.types import NonNegativeInt, StrictStr

from app.schemas.row import RowOut


class SectionInput(BaseModel):
    """Compact section definition supplied by a caller."""

    name: Annotated[
        StrictStr,
        Field(min_length=1, description="Venue section identifier.", examples=["101"]),
    ]
    code: Annotated[
        StrictStr,
        Field(
            min_length=1,
            description="Progression code for this section.",
            examples=["AA:DD,A:C,1:12,13=13W"],
        ),
    ]

    model_config = ConfigDict(
        title="SectionInput",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [{"name": "101", "code": "AA:DD,A:C,1:12,13=13W"}]
        },
    )


class SectionOut(BaseModel):
    """Expanded section with concrete returned rows."""

    name: Annotated[
        StrictStr,
        Field(min_length=1, description="Venue section identifier.", examples=["101"]),
    ]
    rows: list[RowOut] = Field(
        default_factory=list,
        description="Expanded rows for this section.",
    )

    @computed_field(return_type=NonNegativeInt)  # type: ignore[prop-decorator]
    @property
    def row_count(self) -> int:
        return len(self.rows)

    model_config = ConfigDict(
        title="SectionOut",
        strict=True,
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "101",
                    "rows": [
                        {"name": "AA", "position": 1},
                        {"name": "BB", "position": 2},
                        {"name": "CC", "position": 3},
                    ],
                    "row_count": 3,
                }
            ]
        },
    )
