"""Modularity and Reusability in Code Generation Schemas"""

from pydantic import BaseModel, conlist, PositiveInt

from app.schemas.shared import SectionName, RowCode
from app.schemas.venue import RowIn


class GenReq(BaseModel):
    """
    Represents a request for code generation.

    This class is used to define the input structure required for a code generation
    request. It includes the section of the code and a list of rows that specify
    corresponding details. The class utilizes validation and constraints to ensure
    correct request formation.

    :ivar section: Defines the section of the code for which the request is made.
    :type section: SectionName
    :ivar rows: A list of rows containing the details of the request. Must have a
        minimum length of one.
    :type rows: conlist(RowIn, min_length=1)
    """

    section: SectionName
    rows: conlist(RowIn, min_length=1)

    model_config = {"title": "GenerateCodeRequest", "strict": True, "extra": "forbid"}


class GenResp(BaseModel):
    """
    Summary of what the class does.

    Represents a response model with attributes specifying a section,
    code, and row count. This class is intended to ensure the response
    conforms strictly to specifications through immutability and strict
    field validation.

    :ivar section: The section name associated with the response.
    :type section: SectionName
    :ivar code: A specific row code representing the response state.
    :type code: RowCode
    :ivar row_count: The number of rows included in the response. It
        must be a positive integer.
    :type row_count: PositiveInt
    """

    section: SectionName
    code: RowCode
    row_count: PositiveInt

    model_config = {"title": "GenerateCodeResponse", "frozen": True, "strict": True}
