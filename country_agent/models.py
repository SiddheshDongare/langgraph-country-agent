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
        """Parse a single country object from the REST Countries v5 API response."""
        names = data.get("names", {}) or {}
        codes = data.get("codes", {}) or {}

        currencies = [
            CurrencyInfo(
                code=c.get("code", ""), name=c.get("name", ""), symbol=c.get("symbol", "") or ""
            )
            for c in (data.get("currencies") or [])
        ]

        # v5 returns languages as a list of objects; the synthesis prompt wants {code: name}
        languages = {
            (lang.get("iso639_3") or lang.get("bcp47") or ""): lang.get("name", "")
            for lang in (data.get("languages") or [])
        }

        coords = data.get("coordinates", {}) or {}
        latlng = [coords["lat"], coords["lng"]] if "lat" in coords and "lng" in coords else []

        return cls(
            name_common=names.get("common", ""),
            name_official=names.get("official", ""),
            capital=[c.get("name", "") for c in (data.get("capitals") or []) if c.get("name")],
            population=data.get("population", 0) or 0,
            currencies=currencies,
            languages=languages,
            region=data.get("region", "") or "",
            subregion=data.get("subregion", "") or "",
            area=(data.get("area") or {}).get("kilometers", 0.0) or 0.0,
            borders=data.get("borders") or [],
            timezones=data.get("timezones") or [],
            continents=data.get("continents") or [],
            flag=(data.get("flag") or {}).get("emoji", "") or "",
            latlng=latlng,
            maps=data.get("links") or {},
            tld=data.get("tlds") or [],
            cca2=codes.get("alpha_2", "") or "",
            cca3=codes.get("alpha_3", "") or "",
            gini=(data.get("economy") or {}).get("gini_coefficient") or {},
            car_side=(data.get("cars") or {}).get("driving_side", "") or "",
        )
