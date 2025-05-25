# ─────────────────────────────  Helpers  ──────────────────────────────
# Constrained types (regex ensures at least one char, no CR/LF)
from pydantic import constr, BaseModel, Field

RowCode = constr(pattern=r"^[^\r\n]+$", strip_whitespace=True)
SectionName = constr(min_length=1, max_length=32, strip_whitespace=True)

# ───────────────────────────  Core Requests  ──────────────────────────
class ParseReq(BaseModel):
    """
    Represents a request to parse a given row-progression code.

    This class is a data model built upon Pydantic's BaseModel to validate
    and enforce the structure for parsing requests. It includes functionality
    to ensure the input adheres to specified constraints, such as strictness
    and prohibition of additional attributes beyond those defined. Primarily
    aimed at applications requiring controlled and safe parsing workflows.

    :ivar code: Row-progression code that will be parsed. This attribute
        must be provided during initialization and complies with the
        RowCode type.
    :type code: RowCode
    """

    code: RowCode = Field(..., description="Row‑progression code")

    model_config = {"title": "ParseRequest", "strict": True, "extra": "forbid"}


class CompareReq(BaseModel):
    """
    Represents a request to compare two RowCode objects.

    This class is a data model used for comparing two instances of the
    `RowCode` type. It ensures strict validation with no additional
    unexpected fields allowed in the object. The title `CompareRequest`
    is used as a descriptor for the model definition.

    :ivar code_a: The first RowCode object to compare.
    :type code_a: RowCode
    :ivar code_b: The second RowCode object to compare.
    :type code_b: RowCode
    """

    code_a: RowCode
    code_b: RowCode

    model_config = {"title": "CompareRequest", "strict": True, "extra": "forbid"}