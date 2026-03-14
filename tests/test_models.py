"""Unit tests for Pydantic models."""

import pytest

from country_agent.models import CountryInfo, CurrencyInfo


def test_country_info_full(india_raw):
    info = CountryInfo.from_api_response(india_raw)

    assert info.name_common == "India"
    assert info.name_official == "Republic of India"
    assert info.capital == ["New Delhi"]
    assert info.population == 1_417_492_000
    assert len(info.currencies) == 1
    assert info.currencies[0] == CurrencyInfo(code="INR", name="Indian rupee", symbol="₹")
    assert info.languages == {"eng": "English", "hin": "Hindi", "tam": "Tamil"}
    assert info.region == "Asia"
    assert info.cca2 == "IN"
    assert info.cca3 == "IND"
    assert info.gini == {"2011": 35.7}
    assert info.car_side == "left"
    assert info.flag == "🇮🇳"


def test_country_info_no_capital(bouvet_raw):
    info = CountryInfo.from_api_response(bouvet_raw)
    assert info.capital == []


def test_country_info_no_currencies(bouvet_raw):
    info = CountryInfo.from_api_response(bouvet_raw)
    assert info.currencies == []


def test_country_info_no_car(bouvet_raw):
    info = CountryInfo.from_api_response(bouvet_raw)
    assert info.car_side == ""


def test_country_info_multiple_currencies():
    raw = {
        "name": {"common": "Test", "official": "Test"},
        "currencies": {
            "USD": {"name": "Dollar", "symbol": "$"},
            "EUR": {"name": "Euro", "symbol": "€"},
        },
    }
    info = CountryInfo.from_api_response(raw)
    codes = {c.code for c in info.currencies}
    assert codes == {"USD", "EUR"}


def test_country_info_missing_keys():
    """from_api_response should not raise on a minimal/empty dict."""
    info = CountryInfo.from_api_response({"name": {"common": "X", "official": "X"}})
    assert info.population == 0
    assert info.capital == []
    assert info.currencies == []
