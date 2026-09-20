import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { bySlug, neighbours } from "@/lib/countries";

type Props = { params: Promise<{ code: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { code } = await params;
  const country = bySlug(code);
  return { title: country ? `Borders of ${country.name}` : "Country not found" };
}

export default async function BordersPage({ params }: Props) {
  const { code } = await params;
  const country = bySlug(code);
  if (!country) notFound();

  const list = neighbours(country);

  return (
    <main>
      <h1 className="mb-4 text-2xl font-semibold">Borders of {country.name}</h1>

      {list.length === 0 ? (
        <p>{country.name} has no land borders.</p>
      ) : (
        <ul className="mb-6 list-disc pl-6">
          {list.map(({ code: neighbourCode, country: neighbour }) => (
            <li key={neighbourCode} className="p-1">
              {neighbour ? (
                <a href={`/countries/${neighbour.slug}`} className="underline">
                  {neighbour.name}
                </a>
              ) : (
                /* Outside the bundled snapshot, so there is no page to link to. */
                <span>{neighbourCode}</span>
              )}
            </li>
          ))}
        </ul>
      )}

      <p>
        <a href={`/countries/${country.slug}`} className="underline">
          Back to {country.name}
        </a>
      </p>
    </main>
  );
}
