import type { Metadata } from "next";
import { bySlug, countries } from "@/lib/countries";
import { readFavourites } from "@/lib/favourites";

export const metadata: Metadata = { title: "Favourites" };

const ERRORS: Record<string, string> = {
  empty: "Choose a country before saving.",
  unknown: "That country is not in the dataset.",
};

export default async function FavouritesPage({
  searchParams,
}: {
  searchParams: Promise<{ saved?: string; error?: string }>;
}) {
  const { saved, error } = await searchParams;
  const favourites = await readFavourites();
  const savedCountry = saved ? bySlug(saved) : undefined;

  return (
    <main>
      <h1 className="mb-4 text-2xl font-semibold">Favourites</h1>

      {savedCountry ? (
        <section
          role="status"
          aria-label="Save confirmation"
          className="mb-4 border p-3"
        >
          <h2 className="font-semibold">Saved</h2>
          <p>{savedCountry.name} is now in your favourites.</p>
        </section>
      ) : null}

      {error && ERRORS[error] ? (
        <p role="alert" className="mb-4 text-red-700">
          {ERRORS[error]}
        </p>
      ) : null}

      {favourites.length === 0 ? (
        <p className="mb-6">No favourites saved yet.</p>
      ) : (
        <ul className="mb-6 list-disc pl-6">
          {favourites.map((slug) => (
            <li key={slug} className="p-1">
              <a href={`/countries/${slug}`} className="underline">
                {bySlug(slug)!.name}
              </a>
            </li>
          ))}
        </ul>
      )}

      {/* No `required` on the select: submitting nothing must reach the server
          so the validation message is a real server response. */}
      <form method="post" action="/api/favourites" className="flex items-end gap-2">
        <div className="flex flex-col gap-1">
          <label htmlFor="slug">Country</label>
          <select id="slug" name="slug" defaultValue="" className="border p-2">
            <option value="">Choose a country</option>
            {countries.map((country) => (
              <option key={country.slug} value={country.slug}>
                {country.name}
              </option>
            ))}
          </select>
        </div>
        <button type="submit" className="border p-2 font-medium">
          Save to favourites
        </button>
      </form>
    </main>
  );
}
