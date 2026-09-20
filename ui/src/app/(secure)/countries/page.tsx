import type { Metadata } from "next";
import { countries, formatPopulation, regions } from "@/lib/countries";
import { Disclosure } from "@/components/disclosure";

export const metadata: Metadata = { title: "Countries" };

export default async function CountriesPage({
  searchParams,
}: {
  searchParams: Promise<{ region?: string }>;
}) {
  const { region } = await searchParams;
  const visible = region ? countries.filter((c) => c.region === region) : countries;

  return (
    <main>
      <h1 className="mb-4 text-2xl font-semibold">Countries</h1>

      {/* Filtering is GET links, not a form: the crawler aborts every non-GET
          request, so a filter form would be dead to it. */}
      <Disclosure label="Filters">
        <h2 className="mb-2 font-semibold">Region</h2>
        <ul className="flex flex-wrap gap-3">
          {regions.map((name) => (
            <li key={name}>
              <a href={`/countries?region=${encodeURIComponent(name)}`} className="underline">
                {name}
              </a>
            </li>
          ))}
          <li>
            {/* "Clear", not "Reset" — reset is on the denylist and would be skipped. */}
            <a href="/countries" className="underline">
              Clear filters
            </a>
          </li>
        </ul>
      </Disclosure>

      <p className="mb-3">
        {region ? `${visible.length} countries in ${region}` : `${visible.length} countries`}
      </p>

      <table className="w-full border-collapse text-left">
        <caption className="sr-only">Countries, with capital, region and population</caption>
        <thead>
          <tr>
            <th scope="col" className="border-b p-2">Name</th>
            <th scope="col" className="border-b p-2">Capital</th>
            <th scope="col" className="border-b p-2">Region</th>
            <th scope="col" className="border-b p-2">Population</th>
          </tr>
        </thead>
        <tbody>
          {visible.map((country) => (
            <tr key={country.slug}>
              <td className="border-b p-2">
                <a href={`/countries/${country.slug}`} className="underline">
                  {country.name}
                </a>
              </td>
              <td className="border-b p-2">{country.capital.join(", ") || "—"}</td>
              <td className="border-b p-2">{country.region}</td>
              <td className="border-b p-2">{formatPopulation(country.population)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {visible.length === 0 ? <p className="mt-3">No countries match that region.</p> : null}
    </main>
  );
}
