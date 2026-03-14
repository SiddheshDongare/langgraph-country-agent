"""End-to-end integration tests for the LangGraph agent (mocked LLM + HTTP)."""

import httpx
import pytest
import respx
from langchain_core.messages import AIMessage, HumanMessage
from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import INDIA_RAW
from country_agent.models import IntentResult
from country_agent.graph import build_graph, AgentState

BASE_URL = "https://restcountries.com/v3.1"


def _make_initial_state(question: str) -> AgentState:
    return {
        "messages": [HumanMessage(content=question)],
        "country_name": None,
        "requested_fields": [],
        "api_response": None,
        "error": None,
    }


# ---------------------------------------------------------------------------
# Node: identify_intent
# ---------------------------------------------------------------------------

def test_identify_intent_success(mocker):
    from country_agent.nodes import identify_intent

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = IntentResult(
        country_name="Germany", requested_fields=["population"]
    )
    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    state = _make_initial_state("What is the population of Germany?")
    result = identify_intent(state)

    assert result["country_name"] == "Germany"
    assert "population" in result["requested_fields"]
    assert result.get("error") is None


def test_identify_intent_no_country(mocker):
    from country_agent.nodes import identify_intent

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = IntentResult(
        country_name="", requested_fields=["general"]
    )
    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    state = _make_initial_state("What is the largest country?")
    result = identify_intent(state)

    assert result.get("error")
    assert "country name" in result["error"].lower()


def test_identify_intent_llm_failure(mocker):
    from country_agent.nodes import identify_intent

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.side_effect = RuntimeError("LLM unavailable")
    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    state = _make_initial_state("What is the capital of France?")
    result = identify_intent(state)

    assert result.get("error")


# ---------------------------------------------------------------------------
# Node: invoke_tool
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@respx.mock
async def test_invoke_tool_success():
    from country_agent.nodes import invoke_tool

    respx.get(f"{BASE_URL}/name/India").mock(
        return_value=httpx.Response(200, json=[INDIA_RAW])
    )
    state = {**_make_initial_state("population"), "country_name": "India"}
    result = await invoke_tool(state)

    assert result.get("error") is None
    assert result["api_response"] is not None
    assert len(result["api_response"]) >= 1


@pytest.mark.asyncio
@respx.mock
async def test_invoke_tool_not_found():
    from country_agent.nodes import invoke_tool

    respx.get(f"{BASE_URL}/name/xyznotacountry").mock(
        return_value=httpx.Response(404)
    )
    state = {**_make_initial_state(""), "country_name": "xyznotacountry"}
    result = await invoke_tool(state)

    assert result.get("error")


# ---------------------------------------------------------------------------
# Node: synthesize_answer
# ---------------------------------------------------------------------------

def test_synthesize_answer_error_path(mocker):
    from country_agent.nodes import synthesize_answer

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="I couldn't find that country.")
    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    state = {
        **_make_initial_state("What is the capital of xyznotacountry?"),
        "error": "No country found matching 'xyznotacountry'.",
        "api_response": None,
        "requested_fields": [],
    }
    result = synthesize_answer(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)


def test_synthesize_answer_happy_path(mocker):
    from country_agent.nodes import synthesize_answer

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="India has a population of 1,417,492,000.")
    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    state = {
        **_make_initial_state("What is the population of India?"),
        "error": None,
        "api_response": [INDIA_RAW],
        "requested_fields": ["population"],
        "country_name": "India",
    }
    result = synthesize_answer(state)

    assert "population" in result["messages"][0].content.lower()


# ---------------------------------------------------------------------------
# Full graph integration
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@respx.mock
async def test_full_graph_population_query(mocker):
    """Full graph run: population of India."""
    respx.get(f"{BASE_URL}/name/India").mock(
        return_value=httpx.Response(200, json=[INDIA_RAW])
    )

    mock_llm = MagicMock()
    # Intent call returns structured output
    mock_llm.with_structured_output.return_value.invoke.return_value = IntentResult(
        country_name="India", requested_fields=["population"]
    )
    # Synthesis call
    mock_llm.invoke.return_value = AIMessage(content="India's population is 1,417,492,000.")

    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    graph = build_graph().compile()
    result = await graph.ainvoke(_make_initial_state("What is the population of India?"))

    final = result["messages"][-1].content
    assert "india" in final.lower() or "population" in final.lower()


@pytest.mark.asyncio
@respx.mock
async def test_full_graph_invalid_country(mocker):
    """Full graph run: unrecognised country → graceful error."""
    respx.get(f"{BASE_URL}/name/xyznotacountry").mock(
        return_value=httpx.Response(404)
    )

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = IntentResult(
        country_name="xyznotacountry", requested_fields=["general"]
    )
    mock_llm.invoke.return_value = AIMessage(
        content="I couldn't find any country matching 'xyznotacountry'. Please check the spelling."
    )

    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    graph = build_graph().compile()
    result = await graph.ainvoke(_make_initial_state("Tell me about xyznotacountry"))

    final = result["messages"][-1].content
    assert len(final) > 0  # some response produced


@pytest.mark.asyncio
async def test_full_graph_no_country_in_query(mocker):
    """Full graph run: no country in question → intent error → synthesis."""
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = IntentResult(
        country_name="", requested_fields=["general"]
    )
    mock_llm.invoke.return_value = AIMessage(
        content="Please mention a specific country in your question."
    )

    mocker.patch("country_agent.nodes.get_settings", return_value=MagicMock(get_llm=lambda: mock_llm))

    graph = build_graph().compile()
    result = await graph.ainvoke(_make_initial_state("What is the biggest country on Earth?"))

    final = result["messages"][-1].content
    assert len(final) > 0
