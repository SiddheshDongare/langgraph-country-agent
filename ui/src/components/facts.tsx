import { formatPopulation, type Country } from "@/lib/countries";

export type FactGroup = { label: string; facts: [string, string][] };

/**
 * The three groups the record page shows. Named to stay clear of the crawler's
 * destructive-word denylist, which would skip "Reset" or "Cancel" outright.
 */
export function factGroups(country: Country): FactGroup[] {
  const gini = Object.entries(country.gini)[0];
  return [
    {
      label: "Overview",
      facts: [
        ["Official name", country.official],
        ["Capital", country.capital.join(", ") || "—"],
        ["Region", country.region],
        ["Subregion", country.subregion],
        ["Population", formatPopulation(country.population)],
        ["Languages", Object.values(country.languages).join(", ")],
      ],
    },
    {
      label: "Geography",
      facts: [
        ["Area", `${formatPopulation(country.area)} km²`],
        ["Continents", country.continents.join(", ")],
        ["Coordinates", country.latlng.join(", ")],
        ["Time zones", country.timezones.join(", ")],
        ["Land borders", String(country.borders.length)],
      ],
    },
    {
      label: "Economy",
      facts: [
        ["Currency", country.currencies.map((c) => `${c.name} (${c.symbol} ${c.code})`).join(", ")],
        ["Gini coefficient", gini ? `${gini[1]} (${gini[0]})` : "—"],
        ["Top-level domain", country.tld.join(", ")],
        ["Country codes", `${country.cca2} / ${country.cca3}`],
      ],
    },
  ];
}

export function FactList({ facts }: { facts: [string, string][] }) {
  return (
    <dl className="grid grid-cols-[12rem_1fr] gap-y-1">
      {facts.map(([term, value]) => (
        <div key={term} className="contents">
          <dt className="font-medium">{term}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}
