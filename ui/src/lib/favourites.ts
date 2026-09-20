import { cookies } from "next/headers";
import { bySlug } from "./countries";

export const FAVOURITES_COOKIE = "qa_favourites";

/**
 * Favourites live in an httpOnly cookie rather than in server memory: the Next
 * app runs as serverless functions, so module-level state is per-invocation and
 * would appear to lose saved countries at random.
 */
export function parse(raw: string | undefined): string[] {
  if (!raw) return [];
  const seen = new Set<string>();
  for (const slug of raw.split(",")) {
    const country = bySlug(slug.trim());
    if (country) seen.add(country.slug);
  }
  return [...seen];
}

export async function readFavourites(): Promise<string[]> {
  const store = await cookies();
  return parse(store.get(FAVOURITES_COOKIE)?.value);
}
