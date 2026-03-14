"""Shared fixtures and sample API data for tests."""

import pytest

INDIA_RAW = {
    "name": {
        "common": "India",
        "official": "Republic of India",
        "nativeName": {"hin": {"common": "भारत", "official": "भारत गणराज्य"}},
    },
    "tld": [".in"],
    "cca2": "IN",
    "cca3": "IND",
    "capital": ["New Delhi"],
    "region": "Asia",
    "subregion": "Southern Asia",
    "population": 1417492000,
    "area": 3287263.0,
    "currencies": {"INR": {"name": "Indian rupee", "symbol": "₹"}},
    "languages": {"eng": "English", "hin": "Hindi", "tam": "Tamil"},
    "borders": ["BGD", "BTN", "CHN", "NPL", "PAK"],
    "timezones": ["UTC+05:30"],
    "continents": ["Asia"],
    "flag": "🇮🇳",
    "latlng": [20.0, 77.0],
    "maps": {
        "googleMaps": "https://goo.gl/maps/WSk3fLwG4vtPQetp7",
        "openStreetMaps": "https://www.openstreetmap.org/relation/304716",
    },
    "gini": {"2011": 35.7},
    "car": {"signs": ["IND"], "side": "left"},
}

BIOT_RAW = {
    "name": {
        "common": "British Indian Ocean Territory",
        "official": "British Indian Ocean Territory",
    },
    "tld": [".io"],
    "cca2": "IO",
    "cca3": "IOT",
    "capital": ["Diego Garcia"],
    "region": "Africa",
    "subregion": "Eastern Africa",
    "population": 0,
    "area": 60.0,
    "currencies": {"USD": {"name": "United States dollar", "symbol": "$"}},
    "languages": {"eng": "English"},
    "borders": [],
    "timezones": ["UTC+06:00"],
    "continents": ["Asia"],
    "flag": "🇮🇴",
    "latlng": [-6.0, 71.5],
    "maps": {},
    "gini": {},
    "car": {"side": "right"},
}

BOUVET_RAW = {
    "name": {"common": "Bouvet Island", "official": "Bouvet Island"},
    "tld": [".bv"],
    "cca2": "BV",
    "cca3": "BVT",
    "capital": [],          # no capital
    "region": "Antarctic",
    "subregion": "",
    "population": 0,
    "area": 49.0,
    "currencies": {},       # no currencies
    "languages": {},
    "borders": [],
    "timezones": ["UTC+01:00"],
    "continents": ["Antarctica"],
    "flag": "🇧🇻",
    "latlng": [-54.43, 3.4],
    "maps": {},
    "gini": {},
    "car": {},
}


@pytest.fixture
def india_raw():
    return INDIA_RAW


@pytest.fixture
def biot_raw():
    return BIOT_RAW


@pytest.fixture
def bouvet_raw():
    return BOUVET_RAW
