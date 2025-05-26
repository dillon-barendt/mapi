from __future__ import annotations

# ── 1. Model‑level markdown ──────────────────────────────────────────
from pydantic import Field, BaseModel


class ParseReq(BaseModel):
    """
    Represents a data model for parsing a row-progression code.

    This class is used to define and validate the structure of the payload
    for the `/parse` endpoint. It includes attributes such as the row-
    progression code that needs to be parsed. Additionally, it provides a
    model configuration for metadata and validation rules. The purpose of
    this class is to ensure the payload conforms to the expected format
    before processing.

    :ivar code: Row-progression code to parse. Accepts values like
        **`AA:DD,3=3W`**, **`A:D`**, etc.
    :type code: str
    """

    code: str = Field(
        ...,
        description="Row‑progression code to parse, e.g. **`AA:DD,3=3W`**",
        examples=["A:D", "1:5:2"],
    )

    model_config = {
        "title": "ParseRequest",
        "description": (
            "Payload for the `/parse` endpoint.  \n"
            "Supports Markdown inside model descriptions as well."
        ),
        "strict": True,
    }
