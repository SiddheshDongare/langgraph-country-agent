import type { Metadata } from "next";
import { countries, formatPopulation } from "@/lib/countries";

export const metadata: Metadata = { title: "Countries" };

export default function CountriesPage() {
  return (
    <main>
      <h1 className="mb-4 text-2xl font-semibold">Countries</h1>

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
          {countries.map((country) => (
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
    </main>
  );
}
