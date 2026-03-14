"""Tool for fetching country data from the REST Countries API."""

import httpx
import structlog
from langchain_core.tools import tool

from country_agent.settings import get_settings

logger = structlog.get_logger(__name__)


def _disambiguate(results: list[dict], country_name: str) -> list[dict]:
    """Prefer exact name.common match; fall back to full result list."""
    needle = country_name.lower().strip()
    exact = [r for r in results if r.get("name", {}).get("common", "").lower() == needle]
    return exact if exact else results


@tool
async def fetch_country_info(country_name: str) -> dict:
    """Fetch country information from the REST Countries API.

    Args:
        country_name: The name of the country to look up (English or native name).

    Returns:
        Dict with 'results' (list of country objects) or 'error' (string message).
    """
    settings = get_settings()
    url = f"{settings.api_base_url}/name/{country_name}"
    log = logger.bind(country_name=country_name, url=url)

    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout_seconds) as client:
            log.info("fetching_country")
            response = await client.get(url)

            if response.status_code == 404:
                log.warning("country_not_found")
                return {
                    "error": f"No country found matching '{country_name}'. Please check the spelling."
                }

            response.raise_for_status()
            data: list[dict] = response.json()
            results = _disambiguate(data, country_name)
            log.info("fetch_success", total_results=len(data), after_filter=len(results))
            return {"results": results}

    except httpx.TimeoutException:
        log.error("api_timeout")
        return {"error": "The country data API timed out. Please try again."}
    except httpx.HTTPStatusError as exc:
        log.error("api_http_error", status_code=exc.response.status_code)
        return {
            "error": f"API returned an error (HTTP {exc.response.status_code}). Please try again."
        }
    except httpx.RequestError as exc:
        log.error("api_request_error", error=str(exc))
        return {"error": "Could not reach the country data API. Please check your connection."}
