import data from "../data/countries.json" with { type: "json" };

export type Currency = { code: string; name: string; symbol: string };

export type Country = {
  slug: string;
  name: string;
  official: string;
  cca2: string;
  cca3: string;
  capital: string[];
  region: string;
  subregion: string;
  population: number;
  area: number;
  currencies: Currency[];
  languages: Record<string, string>;
  timezones: string[];
  continents: string[];
  latlng: number[];
  tld: string[];
  gini: Record<string, number>;
  /** Neighbour alpha-3 codes, as stored on CountryInfo in country_agent/models.py. */
  borders: string[];
};

/**
 * A committed snapshot, deliberately not the live REST Countries API: the
 * crawler has to read the same DOM every walk so that reported drift means the
 * app changed. The /ask page keeps the live API.
 */
// ponytail: JSON import widens to a union of literal shapes; one cast beats a codegen step.
export const countries = data as unknown as Country[];

const bySlugIndex = new Map(countries.map((c) => [c.slug, c]));
const byCca3Index = new Map(countries.map((c) => [c.cca3, c]));

export function bySlug(slug: string): Country | undefined {
  return bySlugIndex.get(slug.toLowerCase());
}

export function byCca3(code: string): Country | undefined {
  return byCca3Index.get(code.toUpperCase());
}

export const regions: string[] = [...new Set(countries.map((c) => c.region))].sort();

/** A neighbour is linkable only when it is itself in the snapshot. */
export type Neighbour = { code: string; country?: Country };

export function neighbours(country: Country): Neighbour[] {
  return country.borders.map((code) => ({ code, country: byCca3(code) }));
}

export function formatPopulation(n: number): string {
  return n.toLocaleString("en-US");
}
