"""LangGraph node functions: identify_intent, invoke_tool, synthesize_answer."""

import json

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from country_agent.models import VALID_FIELDS, CountryInfo, IntentResult
from country_agent.settings import get_settings
from country_agent.tools import fetch_country_info

logger = structlog.get_logger(__name__)

_INTENT_SYSTEM = """\
You are an intent extraction assistant. Your job is to parse a user's question \
about a country and extract two things:
1. The country name (exactly as the user wrote it, preserving non-English names).
2. The specific information fields the user wants.

Valid field values: {fields}

Rules:
- If the user asks a broad question ("Tell me about France"), use ["general"].
- If you cannot identify any country name, set country_name to an empty string.
- Normalize requested_fields to valid values only; map anything unrecognised to "general".
""".format(fields=", ".join(sorted(VALID_FIELDS)))

_SYNTHESIS_SYSTEM = """\
You are a country information assistant. Answer the user's question using ONLY \
the structured country data provided. Do not invent or guess any facts.

Guidelines:
- Format large numbers with commas (e.g. 1,417,492,000).
- If multiple countries are in the data, identify the most relevant one based on \
the user's question and focus your answer on it (you may briefly note others exist).
- If a requested field is absent or empty in the data, say so honestly.
- Be concise but complete.
"""

_SYNTHESIS_USER_TMPL = """\
User question: {question}

Requested fields: {fields}

Country data (JSON):
{data}
"""

_ERROR_SYNTHESIS_SYSTEM = """\
You are a helpful assistant. The user asked a question about countries, but an \
error occurred. Explain the issue politely and suggest what they can try.
"""


def _build_country_context(api_response: list[dict], requested_fields: list[str]) -> str:
    """Convert raw API dicts to validated CountryInfo JSON for the synthesis prompt."""
    countries = []
    for raw in api_response:
        try:
            info = CountryInfo.from_api_response(raw)
            countries.append(info.model_dump())
        except Exception:
            countries.append(raw)
    return json.dumps(countries, ensure_ascii=False, indent=2)


def identify_intent(state: dict) -> dict:
    """Node 1: Extract country name and requested fields from the user's message."""
    log = logger.bind(node="identify_intent")
    log.info("enter")

    messages = state["messages"]
    user_msg = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)),
        None,
    )
    if not user_msg:
        return {"error": "No user message found in conversation."}

    settings = get_settings()
    llm = settings.get_llm().with_structured_output(IntentResult)

    try:
        result: IntentResult = llm.invoke(
            [SystemMessage(content=_INTENT_SYSTEM), HumanMessage(content=user_msg.content)]
        )
        log.info("intent_extracted", country=result.country_name, fields=result.requested_fields)
    except Exception as exc:
        log.error("intent_extraction_failed", error=str(exc))
        return {"error": f"Could not parse your question: {exc}"}

    if not result.country_name.strip():
        return {
            "error": "I couldn't identify a country name in your question. Please mention a specific country."
        }

    # Normalise fields — drop anything not in the valid set
    valid = [f for f in result.requested_fields if f in VALID_FIELDS] or ["general"]

    return {"country_name": result.country_name, "requested_fields": valid, "error": None}


async def invoke_tool(state: dict) -> dict:
    """Node 2: Call the REST Countries API with the extracted country name."""
    log = logger.bind(node="invoke_tool", country=state.get("country_name"))
    log.info("enter")

    result = await fetch_country_info.ainvoke({"country_name": state["country_name"]})

    if "error" in result:
        log.warning("tool_error", error=result["error"])
        return {"error": result["error"]}

    log.info("tool_success", count=len(result["results"]))
    return {"api_response": result["results"], "error": None}


def synthesize_answer(state: dict) -> dict:
    """Node 3: Generate a natural-language answer grounded in the API data."""
    log = logger.bind(node="synthesize_answer")
    log.info("enter", has_error=bool(state.get("error")))

    settings = get_settings()
    llm = settings.get_llm()

    messages = state["messages"]
    user_msg = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)),
        None,
    )
    question = user_msg.content if user_msg else ""

    # Error path — explain the problem to the user
    if state.get("error"):
        response = llm.invoke(
            [
                SystemMessage(content=_ERROR_SYNTHESIS_SYSTEM),
                HumanMessage(content=f"User question: {question}\n\nError: {state['error']}"),
            ]
        )
        return {"messages": [AIMessage(content=response.content)]}

    # Happy path — synthesize from API data
    context = _build_country_context(
        state["api_response"],
        state.get("requested_fields", ["general"]),
    )
    user_content = _SYNTHESIS_USER_TMPL.format(
        question=question,
        fields=", ".join(state.get("requested_fields", ["general"])),
        data=context,
    )

    try:
        response = llm.invoke(
            [
                SystemMessage(content=_SYNTHESIS_SYSTEM),
                HumanMessage(content=user_content),
            ]
        )
        log.info("synthesis_complete")
        return {"messages": [AIMessage(content=response.content)]}
    except Exception as exc:
        log.error("synthesis_failed", error=str(exc))
        return {
            "messages": [
                AIMessage(
                    content="I retrieved the data but couldn't format the answer. Please try again."
                )
            ]
        }
