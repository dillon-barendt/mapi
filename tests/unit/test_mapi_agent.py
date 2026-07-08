import pytest

from app.agents.mapi import build_agent_analysis, run_mapi_agent
from app.schemas.agent import MapiAgentRequest


def test_build_agent_analysis_explains_mapi_name_and_mapping_value() -> None:
    analysis = build_agent_analysis(
        MapiAgentRequest(
            venue_id="demo-arena",
            section_id="101",
            code="AA:CC,1=1W",
        )
    )

    assert "mapping API" in analysis.friendly_name
    assert "maps venue maps" in analysis.friendly_name
    assert "normalized source value" in analysis.mapping_value_summary
    assert analysis.parser_confidence == "valid"
    assert analysis.redis.string_key == "venue:demo-arena:section:101:row_progression"
    assert any(
        "Equivalent row alias" in trigger for trigger in analysis.review_triggers
    )


@pytest.mark.anyio
async def test_run_mapi_agent_returns_parser_grounded_response() -> None:
    response = await run_mapi_agent(
        MapiAgentRequest(
            venue_id="demo-arena",
            section_id="101",
            code="A,B:C!,D",
            question="What should review focus on?",
        )
    )

    assert response.agent_model == "function:mapi-local"
    assert [(row.name, row.position) for row in response.rows] == [("A", 1), ("D", 4)]
    assert response.stats.total_rows == 2
    assert response.stats.unique_position_count == 2
    assert response.usage_input_tokens > 0
    assert response.usage_output_tokens > 0
    assert any(
        "Gap positions" in trigger for trigger in response.analysis.review_triggers
    )
