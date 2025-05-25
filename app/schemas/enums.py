from enum import Enum


class SegmentKind(str, Enum):
    """
    Represents different kinds of segments in a specific context.

    This Enum is used to categorize segments based on their characteristics
    or relationships. The possible segment kinds are: slice, single,
    equivalent, and gap. Each kind has a specific meaning and application
    in its respective domain.
    """
    slice = "slice"
    single = "single"
    equivalent = "equivalent"
    gap = "gap"