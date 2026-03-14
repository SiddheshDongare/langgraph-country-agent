"""LangGraph StateGraph definition and compilation."""

from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from country_agent.nodes import identify_intent, invoke_tool, synthesize_answer


class AgentState(TypedDict):
    """State shared across all graph nodes."""

    messages: Annotated[list[AnyMessage], add_messages]
    country_name: str | None
    requested_fields: list[str]
    api_response: list[dict] | None
    error: str | None


def _route_after_intent(state: AgentState) -> str:
    """Skip tool invocation if intent extraction failed."""
    if state.get("error") or not state.get("country_name"):
        return "synthesize_answer"
    return "invoke_tool"


def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("identify_intent", identify_intent)
    builder.add_node("invoke_tool", invoke_tool)
    builder.add_node("synthesize_answer", synthesize_answer)

    builder.add_edge(START, "identify_intent")
    builder.add_conditional_edges(
        "identify_intent",
        _route_after_intent,
        ["invoke_tool", "synthesize_answer"],
    )
    builder.add_edge("invoke_tool", "synthesize_answer")
    builder.add_edge("synthesize_answer", END)

    return builder


graph = build_graph().compile()
