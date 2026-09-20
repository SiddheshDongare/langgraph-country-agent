import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { bySlug } from "@/lib/countries";
import { FactList, factGroups } from "@/components/facts";
import { Tabs } from "@/components/tabs";

type Props = { params: Promise<{ code: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { code } = await params;
  const country = bySlug(code);
  return { title: country ? country.name : "Country not found" };
}

export default async function CountryPage({ params }: Props) {
  const { code } = await params;
  const country = bySlug(code);
  if (!country) notFound();

  return (
    <main>
      <h1 className="mb-4 text-2xl font-semibold">{country.name}</h1>

      <Tabs
        label="Country details"
        panels={factGroups(country).map((group) => ({
          label: group.label,
          content: <FactList facts={group.facts} />,
        }))}
      />

      <p className="mb-6">
        <a href={`/countries/${country.slug}/borders`} className="underline">
          Borders of {country.name}
        </a>
      </p>

      {/* A real POST, so the crawler never reaches the confirmation. */}
      <form method="post" action="/api/favourites">
        <input type="hidden" name="slug" value={country.slug} />
        <button type="submit" className="border p-2 font-medium">
          Save to favourites
        </button>
      </form>
    </main>
  );
}
