"""Definitions of row-related items (RowOut, RowProgression, plus any internal helpers)."""

from typing import Annotated, Sequence

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from pydantic.types import StrictStr, PositiveInt

RowName = Annotated[
    StrictStr, Field(..., description="Row identifier (letters / numbers / mixed)")
]


class RowOut(BaseModel):
    """🪑 RowOut – immutable (name, position) tuple."""

    name: RowName
    position: PositiveInt  # 1‑based index

    model_config = ConfigDict(title="RowOut", strict=True, frozen=True)


class RowProgression(BaseModel):
    """RowProgression – original code plus fully‑expanded rows list."""

    code: StrictStr = Field(..., description="Original progression code string.")
    rows: Sequence[RowOut]

    model_config = ConfigDict(title="RowProgression", strict=True, frozen=True)
