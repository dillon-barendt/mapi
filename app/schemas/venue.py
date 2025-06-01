from typing import Annotated, Sequence, Dict
from pydantic import BaseModel, Field, field_validator, computed_field
from pydantic.types import StrictStr, NonNegativeInt
from pydantic.config import ConfigDict

from .section import SectionOut, SectionInput


class VenueRequest(BaseModel):
    """
    Representation of a request to define or modify a venue and its associated sections.

    This class is used to encapsulate the details of a venue, including its name
    and the sections it contains. Each venue must have a uniquely identifiable name,
    and each section within the venue must also have a unique name
    to prevent conflicts or ambiguity.

    :ivar venue_name: Name of the venue.
    :type venue_name: str
    :ivar sections: List of sections in this venue, along with their progression
        codes, ensuring no duplicate section names.
    :type sections: Sequence[SectionInput]
    """

    venue_name: Annotated[StrictStr, Field(min_length=1)] = Field(
        ..., description="Name of the venue."
    )
    sections: Annotated[
        Sequence[SectionInput],
        Field(
            min_length=1,
            description="List of sections in this venue, with progression codes.",
        ),
    ]

    @field_validator("sections")
    @classmethod
    def _verify_unique_sections(
        cls, section_inputs: Sequence[SectionInput]
    ) -> Sequence[SectionInput]:
        def _find_duplicated_names(names: Sequence[str]) -> set[str]:
            return {name for name in names if names.count(name) > 1}

        section_names = [section.name for section in section_inputs]
        duplicates = _find_duplicated_names(section_names)
        if duplicates:
            raise ValueError(
                f"Duplicate section names: {', '.join(sorted(duplicates))}"
            )
        return section_inputs


class VenueOut(BaseModel):
    venue_name: Annotated[
        StrictStr,
        Field(min_length=1, description="Name of the venue."),
    ]
    sections: Annotated[
        Sequence[SectionOut],
        Field(
            min_length=1,
            description="List of sections in this venue, with expanded rows.",
        ),
    ]
    # Remove the regular field here:
    # total_rows: Annotated[NonNegativeInt, Field(default=0, description="...")]

    @computed_field(return_type=NonNegativeInt)
    @property
    def total_rows(self) -> NonNegativeInt:
        return sum(section.row_count for section in self.sections)


class Venue(BaseModel):
    """
    Represents a venue with a name and associated sections.

    This class is designed to define a venue entity with a specific name
    and a collection of sections. Each section has a name and corresponding
    progression code. It enforces strict validation rules on the data provided
    to ensure consistency and correctness. The configuration of this model
    disallows extra fields and requires a strict mapping for defined attributes.

    :ivar name: The name of the venue.
    :type name: StrictStr
    :ivar sections: A dictionary mapping section names to progression codes.
    :type sections: Dict[StrictStr, StrictStr]
    """

    name: Annotated[
        StrictStr,
        Field(
            min_length=1,
            description="Name of the venue.",
        ),
    ]
    sections: Dict[StrictStr, StrictStr]  # section name → progression code

    model_config = ConfigDict(title="Venue", strict=True, extra="forbid")


class VenueDiffReq(BaseModel):
    """
    Represents a data model for comparing two venues.

    This class is used for encapsulating two `Venue` objects to enable detailed
    comparison or operations between them. It inherits from `BaseModel` and
    enforces strict validation rules to ensure its data integrity.

    :ivar a: The first `Venue` object to compare.
    :type a: Venue
    :ivar b: The second `Venue` object to compare.
    :type b: Venue
    """

    a: Venue
    b: Venue

    model_config = ConfigDict(title="VenueDiffReq", strict=True, extra="forbid")
