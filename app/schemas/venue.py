# ─────────────────────  Venue‑building models  ────────────────────────
from typing import List, Dict

from pydantic import (
    BaseModel,
    field_validator,
    conlist,
    Field,
    StrictStr,
    PositiveInt,
    model_validator,
    computed_field,
)

from app.schemas.shared import SectionName, RowCode


class SectionInput(BaseModel):
    """
    Represents input parameters for defining a section.

    This class serves as a data model for encapsulating details related to a specific
    section, such as its name and code. The configuration enforces strict validation
    rules, making it suitable for scenarios where accurate data representation is
    critical.

    :ivar name: Represents the name of the section. Examples may include names like
        "101" or "Balcony‑L".
    :type name: SectionName
    :ivar code: Refers to the designated code identifying this section.
    :type code: RowCode
    """

    name: SectionName = Field(..., examples=["101", "Balcony‑L"])
    code: RowCode

    model_config = {"title": "SectionInput", "strict": True, "extra": "forbid"}


class VenueRequest(BaseModel):
    """
    Represents a request for configuring a venue with specified sections.

    This class is used to define the structure of a venue request, including
    its name and sections. The venue name must be a strict string, and the
    sections must be a list with a minimum length of 1. The class ensures
    the uniqueness of section names using a validator.

    :ivar venue_name: Name of the venue.
    :type venue_name: StrictStr
    :ivar sections: A list of sections within the venue. Each section is defined
        as an instance of `SectionInput`. The list must have a minimum length of 1.
    :type sections: List[SectionInput]
    """

    venue_name: StrictStr = Field(..., examples=["Big Bowl Stadium"])
    sections: conlist(SectionInput, min_length=1)

    model_config = {"title": "VenueRequest", "strict": True, "extra": "forbid"}

    @field_validator("sections")
    @classmethod
    def unique_sections(cls, v: List[SectionInput]) -> List[SectionInput]:
        names = [s.name for s in v]
        if len(names) != len(set(names)):
            dupes = set(n for n in names if names.count(n) > 1)
            raise ValueError(f"Duplicate section names: {dupes}")
        return v


# ───────────────────  Row / Section output helpers  ───────────────────
class RowOut(BaseModel):
    """
    Represents a data model for a row with specified constraints.

    Provides a structure to store the name and position information for a row
    with enforced strict types and configurations. This model is designed to be
    frozen and compliant with strict validation rules for its fields. Useful for
    cases where immutability and strict data validation are required.

    :ivar name: The name of the row.
    :type name: StrictStr
    :ivar position: The position index of the row, which must be a positive integer.
    :type position: PositiveInt
    """

    name: StrictStr
    position: PositiveInt

    model_config = {"title": "Row", "frozen": True, "strict": True}


class SectionOut(BaseModel):
    """
    Represents a section with a name and a list of rows. Provides additional computed
    properties for ease of access and data management.

    The `SectionOut` class is designed to encapsulate detailed information about a
    specific section including its name, rows, and count of rows. This class
    includes a computed property to dynamically compute the number of rows.
    It ensures immutability and strict validation for data integrity by leveraging
    model configuration.

    :ivar name: Specifies the name of the section.
    :type name: SectionName
    :ivar rows: Contains the list of rows associated with the section.
    :type rows: List[RowOut]
    """

    name: SectionName
    rows: List[RowOut]

    model_config = {"title": "SectionOut", "frozen": True, "strict": True}

    @computed_field
    @property
    def row_count(self) -> int:
        return len(self.rows)


class VenueOut(BaseModel):
    """
    Represents an expanded venue with canonical row positions.

    This class is used to model venue details including its name, sections, and
    the total number of rows. The model enforces strict validation rules to ensure
    consistency, particularly between the specified total rows and the calculated
    sum of rows across all sections.

    :ivar venue_name: The name of the venue.
    :type venue_name: StrictStr
    :ivar sections: A list of sections in the venue. Each section contains details
        about its rows and other properties.
    :type sections: List[SectionOut]
    :ivar total_rows: The total number of rows across all sections in the venue.
    :type total_rows: PositiveInt
    """

    venue_name: StrictStr
    sections: List[SectionOut]
    total_rows: PositiveInt

    model_config = {
        "title": "VenueOut",
        "description": "Expanded venue with canonical row positions",
        "frozen": True,
        "strict": True,
    }

    @model_validator(mode="after")
    def validate_totals(self) -> "VenueOut":
        calc = sum(sec.row_count for sec in self.sections)
        if calc != self.total_rows:
            raise ValueError(f"total_rows={self.total_rows} but sums to {calc}")
        return self


# ────────────────────  Venue‑diff & generator  ────────────────────────
class Venue(BaseModel):
    """
    Represents a venue with its associated sections.

    This class provides a structure to define a venue by its name and a dictionary
    that maps section names to their corresponding row codes. It enforces strict
    validation on the input data to ensure compliance with the model configuration.
    The class is restrictive in terms of additional fields, ensuring the integrity
    of the data represented.

    :ivar name: The name of the venue.
    :type name: StrictStr
    :ivar sections: A dictionary mapping section names (keys) to their corresponding
        row codes (values).
    :type sections: Dict[SectionName, RowCode]
    """

    name: StrictStr
    sections: Dict[SectionName, RowCode]

    model_config = {"title": "VenueCompact", "strict": True, "extra": "forbid"}


class VenueDiffReq(BaseModel):
    """
    Represents a request to compute the difference between two venues.

    This class facilitates the comparison of two `Venue` objects. It is used as a
    structured input model to define the attributes required for comparing venues.
    The request is set up to be strict and does not allow extra fields apart from
    the defined attributes.

    :ivar a: The first venue object to be compared.
    :type a: Venue
    :ivar b: The second venue object to be compared.
    :type b: Venue
    """

    a: Venue
    b: Venue

    model_config = {"title": "VenueDiffRequest", "strict": True, "extra": "forbid"}


class RowIn(BaseModel):
    """
    Represents a model for input data validation of a row.

    This class enforces strict validation on its attributes and is configured
    to disallow any extra fields by default. It serves as a data structure
    for defining and validating the attributes of a row entry, with strict
    types defined for each attribute.

    :ivar name: The name associated with the row.
    :type name: StrictStr
    :ivar position: The position number associated with the row.
    :type position: PositiveInt
    """

    name: StrictStr
    position: PositiveInt

    model_config = {"title": "RawRowInput", "strict": True, "extra": "forbid"}
