from pydantic import BaseModel, StrictStr, PositiveInt

from app.schemas.enums import SegmentKind
from app.schemas.shared import RowCode


class SliceInfoReq(BaseModel):
    """
    Represents a request for slice information in a system.

    This class is utilized to structure and enforce correct data for
    sending a request to retrieve or interact with slice-related
    information. It is based on `BaseModel` and provides configurations
    for strict type validation, a specific title, and forbidden
    additional fields.

    :ivar code: Represents a code related to the slice information request.
    :type code: RowCode
    """

    code: RowCode

    model_config = {"title": "SliceInfoRequest", "strict": True, "extra": "forbid"}


class SliceOut(BaseModel):
    """
    Represents a segment in a text with a defined type and range.

    This class provides structure for a segment, defining the type of the
    segment, its textual content, and its starting and ending positions
    within a larger context. It is designed to be immutable (`frozen: True`)
    and adheres to strict attribute validation, as indicated by the
    configuration settings.

    :ivar kind: The kind of segment represented.
    :type kind: SegmentKind
    :ivar text: The text content of the segment.
    :type text: StrictStr
    :ivar start: The starting position of the segment in the text.
    :type start: PositiveInt
    :ivar end: The ending position of the segment in the text.
    :type end: PositiveInt
    """

    kind: SegmentKind
    text: StrictStr
    start: PositiveInt
    end: PositiveInt

    model_config = {"title": "SliceSegment", "frozen": True, "strict": True}
