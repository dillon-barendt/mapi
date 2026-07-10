from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import NonNegativeInt, StrictStr

from .code import StatsResp
from .row import RowOut


class MapiAgentRequest(BaseModel):
    """Request for the Mapi venue-mapping agent."""

    code: Annotated[
        StrictStr,
        Field(
            min_length=1,
            description="Compact row progression code to inspect.",
            examples=["AA:DD,A:C,1:12,13=13W"],
        ),
    ]
    venue_id: StrictStr | None = Field(
        default=None,
        description="Optional synthetic venue identifier for cache/key suggestions.",
        examples=["demo-arena"],
    )
    section_id: StrictStr | None = Field(
        default=None,
        description="Optional synthetic section identifier for cache/key suggestions.",
        examples=["101"],
    )
    question: StrictStr | None = Field(
        default=None,
        description="Optional operator question for the agent to address.",
        examples=["What should a broker review before publishing this section?"],
    )

    model_config = ConfigDict(
        title="MapiAgentRequest",
        strict=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "venue_id": "demo-arena",
                    "section_id": "101",
                    "code": "AA:DD,A:C,1:12,13=13W",
                    "question": "What changed-risk should an inventory workflow watch?",
                }
            ]
        },
    )


class RedisMappingSuggestion(BaseModel):
    """Redis key suggestions for a compact venue mapping."""

    string_key: StrictStr
    hash_key: StrictStr
    json_key: StrictStr
    index_document_key: StrictStr

    model_config = ConfigDict(
        title="RedisMappingSuggestion",
        strict=True,
        extra="forbid",
    )


class MapiAgentAnalysis(BaseModel):
    """Structured interpretation produced by the Mapi agent."""

    friendly_name: StrictStr = Field(
        ...,
        description="Human-readable explanation of the name Mapi.",
        examples=[
            (
                "Mapi is a friendly name for mapping API, mapping venue maps, "
                "and mapping normalized values."
            )
        ],
    )
    domain_summary: StrictStr = Field(
        ...,
        description="Short explanation of what the submitted row progression means.",
    )
    mapping_value_summary: StrictStr = Field(
        ...,
        description="Why this compact code is useful as a normalized mapping value.",
    )
    parser_confidence: Literal["valid", "invalid"]
    review_triggers: list[StrictStr] = Field(
        default_factory=list,
        description="Reasons an agent or human workflow should inspect this section.",
    )
    redis: RedisMappingSuggestion
    recommended_next_actions: list[StrictStr] = Field(
        default_factory=list,
        description="Practical next steps for inventory, marketplace, or review flows.",
    )

    model_config = ConfigDict(
        title="MapiAgentAnalysis",
        strict=True,
        extra="forbid",
    )


class MapiAgentResp(BaseModel):
    """Pydantic AI-backed agent response for one compact row progression."""

    analysis: MapiAgentAnalysis
    rows: list[RowOut]
    stats: StatsResp
    agent_model: StrictStr = Field(
        ...,
        description="Pydantic AI model used for this run.",
        examples=["function:mapi-local"],
    )
    usage_input_tokens: NonNegativeInt
    usage_output_tokens: NonNegativeInt

    model_config = ConfigDict(
        title="MapiAgentResp",
        strict=True,
        extra="forbid",
    )
