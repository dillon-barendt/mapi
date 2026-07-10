from __future__ import annotations

import json
from collections.abc import Sequence

from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel

from mapi.schemas import validators as row_progression
from mapi.schemas.agent import (
    MapiAgentAnalysis,
    MapiAgentRequest,
    MapiAgentResp,
    RedisMappingSuggestion,
)
from mapi.schemas.code import StatsResp
from mapi.schemas.row import RowOut

MAPI_AGENT_INSTRUCTIONS = """
You are Mapi, a venue mapping agent.

Mapi means:
- mapping venue maps into typed section-row models;
- mapping compact DSL values into normalized, comparable infrastructure values;
- exposing that work through an API.

Explain mapping risk plainly. Do not claim production usage. Use synthetic venue
and section identifiers only.
"""


def _redis_suggestions(venue_id: str, section_id: str) -> RedisMappingSuggestion:
    base = f"venue:{venue_id}:section:{section_id}"
    return RedisMappingSuggestion(
        string_key=f"{base}:row_progression",
        hash_key=base,
        json_key=f"{base}:expanded",
        index_document_key=f"{base}:index",
    )


def _has_position_aliases(rows: Sequence[RowOut]) -> bool:
    positions = [row.position for row in rows]
    return len(positions) != len(set(positions))


def _has_position_gaps(rows: Sequence[RowOut]) -> bool:
    positions = {row.position for row in rows}
    return bool(positions) and max(positions) != len(positions)


def _review_triggers(code: str, rows: Sequence[RowOut]) -> list[str]:
    triggers: list[str] = []
    if "=" in code:
        triggers.append("Equivalent row alias detected; verify shared-position rows.")
    if "!" in code or _has_position_gaps(rows):
        triggers.append(
            "Gap positions detected; confirm neighboring-section alignment."
        )
    if ":" in code:
        triggers.append(
            "Range expansion used; validate start/end row family semantics."
        )
    if any(
        any(char.isdigit() for char in row.name) and not row.name.isdigit()
        for row in rows
    ):
        triggers.append(
            "Mixed row codes detected; keep them atomic and do not range them."
        )
    return triggers


def _next_actions(triggers: Sequence[str]) -> list[str]:
    actions = [
        "Cache the compact code as the source value and expanded rows as a derivative.",
        "Index row count, gap presence, and alias presence for review workflows.",
    ]
    if triggers:
        actions.append(
            "Route triggered conditions to a human review queue before publishing."
        )
    else:
        actions.append("Treat this section as low-risk after parser validation.")
    return actions


def build_agent_analysis(req: MapiAgentRequest) -> MapiAgentAnalysis:
    rows = row_progression.parse_code(req.code)
    stats = row_progression.get_stats(req.code)
    venue_id = req.venue_id or "demo-venue"
    section_id = req.section_id or "demo-section"
    triggers = _review_triggers(req.code, rows)

    question_context = f" Operator question: {req.question}" if req.question else ""

    return MapiAgentAnalysis(
        friendly_name=(
            "Mapi is a friendly name for a mapping API: it maps venue maps, "
            "maps compact DSL values into typed infrastructure values, and exposes "
            "those mappings through FastAPI."
        ),
        domain_summary=(
            f"Section {section_id} expands to {len(rows)} returned row names across "
            f"{stats['unique_position_count']} physical positions.{question_context}"
        ),
        mapping_value_summary=(
            "The compact row progression is the normalized source value. Expanded "
            "rows, stats, diffs, and Redis index fields are deterministic derivatives."
        ),
        parser_confidence="valid",
        review_triggers=triggers,
        redis=_redis_suggestions(venue_id, section_id),
        recommended_next_actions=_next_actions(triggers),
    )


def build_mapi_agent(output_text: str) -> Agent[None, str]:
    model = FunctionModel(
        lambda _messages, _agent_info: ModelResponse(
            parts=[TextPart(content=output_text)]
        ),
        model_name="function:mapi-local",
    )
    return Agent(
        model,
        output_type=str,
        instructions=MAPI_AGENT_INSTRUCTIONS,
        name="mapi-agent",
    )


async def run_mapi_agent(req: MapiAgentRequest) -> MapiAgentResp:
    rows = row_progression.parse_code(req.code)
    stats = StatsResp(**row_progression.get_stats(req.code))
    analysis = build_agent_analysis(req)

    agent = build_mapi_agent(analysis.model_dump_json())
    result = await agent.run(
        json.dumps(
            {
                "code": req.code,
                "venue_id": req.venue_id,
                "section_id": req.section_id,
                "question": req.question,
            }
        )
    )
    output = MapiAgentAnalysis.model_validate_json(result.output)
    usage = result.usage
    agent_model = result.response.model_name or "function:mapi-local"

    return MapiAgentResp(
        analysis=output,
        rows=rows,
        stats=stats,
        agent_model=agent_model,
        usage_input_tokens=usage.input_tokens or 0,
        usage_output_tokens=usage.output_tokens or 0,
    )
