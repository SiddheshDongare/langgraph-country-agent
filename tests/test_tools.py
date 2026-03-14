"""Unit tests for the fetch_country_info tool (mocked HTTP via respx)."""

import httpx
import pytest
import respx

from tests.conftest import BIOT_RAW, INDIA_RAW
from country_agent.tools import fetch_country_info, _disambiguate


# ---------------------------------------------------------------------------
# _disambiguate helper
# ---------------------------------------------------------------------------

def test_disambiguate_exact_match():
    results = [INDIA_RAW, BIOT_RAW]
    filtered = _disambiguate(results, "India")
    assert len(filtered) == 1
    assert filtered[0]["name"]["common"] == "India"


def test_disambiguate_case_insensitive():
    results = [INDIA_RAW, BIOT_RAW]
    filtered = _disambiguate(results, "india")
    assert len(filtered) == 1
    assert filtered[0]["name"]["common"] == "India"


def test_disambiguate_no_exact_match_returns_all():
    results = [INDIA_RAW, BIOT_RAW]
    filtered = _disambiguate(results, "ind")
    assert len(filtered) == 2


def test_disambiguate_single_result():
    results = [INDIA_RAW]
    filtered = _disambiguate(results, "India")
    assert filtered == [INDIA_RAW]


# ---------------------------------------------------------------------------
# fetch_country_info tool
# ---------------------------------------------------------------------------

BASE_URL = "https://restcountries.com/v3.1"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_success_exact_match():
    respx.get(f"{BASE_URL}/name/India").mock(
        return_value=httpx.Response(200, json=[INDIA_RAW, BIOT_RAW])
    )
    result = await fetch_country_info.ainvoke({"country_name": "India"})
    assert "results" in result
    # Disambiguated to just India
    assert len(result["results"]) == 1
    assert result["results"][0]["name"]["common"] == "India"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_404():
    respx.get(f"{BASE_URL}/name/xyznotacountry").mock(
        return_value=httpx.Response(404, json={"status": 404, "message": "Not Found"})
    )
    result = await fetch_country_info.ainvoke({"country_name": "xyznotacountry"})
    assert "error" in result
    assert "xyznotacountry" in result["error"]


@pytest.mark.asyncio
@respx.mock
async def test_fetch_timeout():
    respx.get(f"{BASE_URL}/name/Germany").mock(side_effect=httpx.TimeoutException("timed out"))
    result = await fetch_country_info.ainvoke({"country_name": "Germany"})
    assert "error" in result
    assert "timed out" in result["error"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_network_error():
    respx.get(f"{BASE_URL}/name/France").mock(side_effect=httpx.RequestError("connection refused"))
    result = await fetch_country_info.ainvoke({"country_name": "France"})
    assert "error" in result
    assert "connection" in result["error"].lower()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_server_error():
    respx.get(f"{BASE_URL}/name/Japan").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    result = await fetch_country_info.ainvoke({"country_name": "Japan"})
    assert "error" in result
    assert "500" in result["error"]
