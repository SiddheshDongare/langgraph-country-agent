"""CLI entry point for the Country Information AI Agent."""

import asyncio
import logging
import sys

import structlog

from country_agent.settings import get_settings


def _configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )


async def _run(question: str) -> str:
    from langchain_core.messages import HumanMessage

    from country_agent.graph import graph

    initial_state = {
        "messages": [HumanMessage(content=question)],
        "country_name": None,
        "requested_fields": [],
        "api_response": None,
        "error": None,
    }
    result = await graph.ainvoke(initial_state)
    return result["messages"][-1].content


def main() -> None:
    _configure_logging()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        try:
            question = input("Ask about a country: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            sys.exit(0)

    if not question:
        print("Please provide a question.")
        sys.exit(1)

    answer = asyncio.run(_run(question))
    print(answer)


if __name__ == "__main__":
    main()
