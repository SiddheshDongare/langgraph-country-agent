"""Pydantic models for intent detection and REST Countries API responses."""

from pydantic import BaseModel, Field

VALID_FIELDS = {
    "population",
    "capital",
    "currencies",
    "languages",
    "region",
    "subregion",
    "area",
    "borders",
    "timezones",
    "continents",
    "flag",
    "latlng",
    "maps",
    "car",
    "gini",
    "tld",
    "cca2",
    "cca3",
    "general",
}


class IntentResult(BaseModel):
    """Structured output from the intent identification node."""

    country_name: str = Field(
        description="The country name extracted from the user's question. "
        "Empty string if no country could be identified."
    )
    requested_fields: list[str] = Field(
        description=(
            "List of information fields the user wants. "
            f"Valid values: {', '.join(sorted(VALID_FIELDS))}. "
            "Use 'general' when the user asks a broad question without specifying fields."
        )
    )


class CurrencyInfo(BaseModel):
    code: str
    name: str
    symbol: str = ""


class CountryInfo(BaseModel):
    """Validated subset of a REST Countries API country object."""

    name_common: str
    name_official: str
    capital: list[str] = Field(default_factory=list)
    population: int = 0
    currencies: list[CurrencyInfo] = Field(default_factory=list)
    languages: dict[str, str] = Field(default_factory=dict)
    region: str = ""
    subregion: str = ""
    area: float = 0.0
    borders: list[str] = Field(default_factory=list)
    timezones: list[str] = Field(default_factory=list)
    continents: list[str] = Field(default_factory=list)
    flag: str = ""
    latlng: list[float] = Field(default_factory=list)
    maps: dict[str, str] = Field(default_factory=dict)
    tld: list[str] = Field(default_factory=list)
    cca2: str = ""
    cca3: str = ""
    gini: dict[str, float] = Field(default_factory=dict)
    car_side: str = ""

    @classmethod
    def from_api_response(cls, data: dict) -> "CountryInfo":
        """Parse a single country object from the REST Countries API response."""
        name = data.get("name", {})

        currencies_raw = data.get("currencies", {}) or {}
        currencies = [
            CurrencyInfo(code=code, name=info.get("name", ""), symbol=info.get("symbol", ""))
            for code, info in currencies_raw.items()
        ]

        car = data.get("car", {}) or {}

        return cls(
            name_common=name.get("common", ""),
            name_official=name.get("official", ""),
            capital=data.get("capital") or [],
            population=data.get("population", 0),
            currencies=currencies,
            languages=data.get("languages") or {},
            region=data.get("region", ""),
            subregion=data.get("subregion", ""),
            area=data.get("area", 0.0) or 0.0,
            borders=data.get("borders") or [],
            timezones=data.get("timezones") or [],
            continents=data.get("continents") or [],
            flag=data.get("flag", ""),
            latlng=data.get("latlng") or [],
            maps=data.get("maps") or {},
            tld=data.get("tld") or [],
            cca2=data.get("cca2", ""),
            cca3=data.get("cca3", ""),
            gini=data.get("gini") or {},
            car_side=car.get("side", ""),
        )
