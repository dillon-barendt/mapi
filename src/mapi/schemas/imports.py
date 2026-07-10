from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import PositiveInt, StrictStr


class RowImportRecord(BaseModel):
    """Spreadsheet-shaped section,row,position record."""

    section: Annotated[
        StrictStr,
        Field(
            min_length=1,
            description="Section identifier from a spreadsheet row.",
            examples=["101"],
        ),
    ]
    row: Annotated[
        StrictStr,
        Field(
            min_length=1,
            description="Row label from a spreadsheet row.",
            examples=["AA"],
        ),
    ]
    position: Annotated[
        PositiveInt,
        Field(
            description="1-based physical row position.",
            examples=[1],
        ),
    ]

    model_config = ConfigDict(title="RowImportRecord", strict=True, extra="forbid")


class RowImportRequest(BaseModel):
    """Batch of spreadsheet-shaped row records."""

    rows: Annotated[
        list[RowImportRecord],
        Field(
            min_length=1,
            description="Spreadsheet-shaped rows to group and compress by section.",
        ),
    ]

    model_config = ConfigDict(
        title="RowImportRequest",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "rows": [
                        {"section": "101", "row": "AA", "position": 1},
                        {"section": "101", "row": "BB", "position": 2},
                        {"section": "101", "row": "13", "position": 20},
                        {"section": "101", "row": "13W", "position": 20},
                    ]
                }
            ]
        },
    )


class RowImportResponse(BaseModel):
    """Compact row progression codes grouped by section."""

    sections: dict[StrictStr, StrictStr] = Field(
        ...,
        description="Mapping of section identifiers to compact row progression codes.",
        examples=[{"101": "AA:BB,3:19!,13=13W"}],
    )

    model_config = ConfigDict(
        title="RowImportResponse",
        strict=True,
        extra="forbid",
    )
