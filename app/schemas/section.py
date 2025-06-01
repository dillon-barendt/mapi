from typing import Sequence, Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic.types import StrictStr, NonNegativeInt
from pydantic.config import ConfigDict
from app.schemas.row import RowOut


class SectionInput(BaseModel):
    """Compact section definition (incoming)."""

    name: Annotated[StrictStr, Field(..., description="Section name")]
    code: Annotated[
        StrictStr, Field(..., description="Progression code for this section")
    ]

    model_config = ConfigDict(title="SectionInput", strict=True, extra="forbid")


class SectionOut(BaseModel):
    """Expanded section with concrete rows."""

    name: StrictStr
    rows: Sequence[RowOut]
    row_count: NonNegativeInt = Field(
        default=0, description="Number of rows in this section."
    )

    @field_validator("row_count", mode="before")
    def _compute_row_count(cls, v, values):  # noqa: ANN001
        return v or len(values.get("rows", []))

    model_config = ConfigDict(title="SectionOut", strict=True, frozen=True)
