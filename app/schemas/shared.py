# ─────────────────────────────  Helpers  ──────────────────────────────
# Constrained types (regex ensures at least one char, no CR/LF)
from pydantic import constr, BaseModel, Field

RowCode = constr(pattern=r"^[^\r\n]+$", strip_whitespace=True)
SectionName = constr(min_length=1, max_length=32, strip_whitespace=True)


# ───────────────────────────  Core Requests  ──────────────────────────
class ParseReq(BaseModel):
    """
    Represents a request to parse, ensuring strict validation and prohibiting any extra attributes
    beyond those explicitly defined.

    This class is built using Pydantic's `BaseModel` and validates the provided data against the
    specified type and field constraints. Designed for scenarios where strict data validation is
    required, it enforces adherence to the expected schema without allowing additional fields
    to be injected.

    :ivar code: Row-progression code that identifies the specific progression behavior.
    :type code: RowCode
    """

    code: RowCode = Field(..., description="Row‑progression code")

    model_config = {"title": "ParseRequest", "strict": True, "extra": "forbid"}


class CompareReq(BaseModel):
    """
    Represents a request for comparing two row codes.

    This class is used to encapsulate the comparison request details,
    including two codes of type RowCode. It defines validation rules and
    configuration through its model configuration attributes.

    :ivar code_a: The first row code to be compared.
    :type code_a: RowCode
    :ivar code_b: The second row code to be compared.
    :type code_b: RowCode
    """

    code_a: RowCode
    code_b: RowCode

    model_config = {"title": "CompareRequest", "strict": True, "extra": "forbid"}
