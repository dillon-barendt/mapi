from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from pydantic.types import NonNegativeInt, PositiveInt, StrictStr

from .section import SectionInput, SectionOut


class VenueRequest(BaseModel):
    """Compact venue request containing section row progression codes."""

    venue_name: Annotated[
        StrictStr,
        Field(
            min_length=1, description="Synthetic venue name.", examples=["Demo Arena"]
        ),
    ]
    sections: Annotated[
        list[SectionInput],
        Field(
            min_length=1,
            description="Sections in this venue with compact progression codes.",
        ),
    ]

    @field_validator("sections")
    @classmethod
    def _verify_unique_sections(
        cls, section_inputs: list[SectionInput]
    ) -> list[SectionInput]:
        section_names = [section.name for section in section_inputs]
        duplicates = {name for name in section_names if section_names.count(name) > 1}
        if duplicates:
            raise ValueError(
                f"Duplicate section names: {', '.join(sorted(duplicates))}"
            )
        return section_inputs

    model_config = ConfigDict(
        title="VenueRequest",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "venue_name": "Demo Arena",
                    "sections": [
                        {"name": "101", "code": "AA:DD,A:C,1:12,13=13W"},
                        {"name": "102", "code": "A,B:C!,D"},
                    ],
                }
            ]
        },
    )


class VenueOut(BaseModel):
    """Expanded venue response."""

    venue_name: Annotated[
        StrictStr,
        Field(
            min_length=1, description="Synthetic venue name.", examples=["Demo Arena"]
        ),
    ]
    sections: Annotated[
        list[SectionOut],
        Field(
            min_length=1,
            description="Sections in this venue with expanded rows.",
        ),
    ]

    @computed_field(return_type=NonNegativeInt)  # type: ignore[prop-decorator]
    @property
    def total_rows(self) -> int:
        return sum(section.row_count for section in self.sections)

    model_config = ConfigDict(
        title="VenueOut",
        strict=True,
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "venue_name": "Demo Arena",
                    "sections": [
                        {
                            "name": "101",
                            "rows": [
                                {"name": "AA", "position": 1},
                                {"name": "BB", "position": 2},
                            ],
                            "row_count": 2,
                        }
                    ],
                    "total_rows": 2,
                }
            ]
        },
    )


class Venue(BaseModel):
    """Compact venue representation used for structural diffs."""

    name: Annotated[
        StrictStr,
        Field(
            min_length=1, description="Synthetic venue name.", examples=["Demo Arena"]
        ),
    ]
    sections: dict[StrictStr, StrictStr] = Field(
        ...,
        min_length=1,
        description="Mapping of section name to row progression code.",
        examples=[{"101": "A:C", "102": "A,B!,C"}],
    )

    model_config = ConfigDict(title="Venue", strict=True, extra="forbid")


class VenueDiffReq(BaseModel):
    """Pair of compact venues to compare."""

    a: Venue
    b: Venue

    model_config = ConfigDict(
        title="VenueDiffReq",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "a": {"name": "Old Demo", "sections": {"101": "A:C"}},
                    "b": {"name": "New Demo", "sections": {"101": "A:B,D"}},
                }
            ]
        },
    )


class RowPositionDelta(BaseModel):
    """Position comparison for one row name."""

    a: PositiveInt | None = Field(
        None,
        description="Position in the first venue, or null when absent.",
        examples=[2],
    )
    b: PositiveInt | None = Field(
        None,
        description="Position in the second venue, or null when absent.",
        examples=[None],
    )

    model_config = ConfigDict(title="RowPositionDelta", strict=True, extra="forbid")


class VenueDiffResp(BaseModel):
    """Venue diff keyed by section name and row name."""

    venue_diff: dict[str, dict[str, RowPositionDelta]] = Field(
        ...,
        description="Changed row positions keyed by section and row name.",
    )

    model_config = ConfigDict(
        title="VenueDiffResp",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "venue_diff": {
                        "101": {
                            "C": {"a": 3, "b": None},
                            "D": {"a": None, "b": 3},
                        }
                    }
                }
            ]
        },
    )
