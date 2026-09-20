import { NextRequest } from "next/server";
import { seeOther } from "@/lib/http";
import { bySlug } from "@/lib/countries";
import { FAVOURITES_COOKIE, readFavourites } from "@/lib/favourites";

/**
 * A real POST, so the crawler cannot reach the confirmation or the validation
 * message: it aborts every non-GET request at the network layer. That is the
 * point of this feature, not a limitation to design around.
 */
export async function POST(request: NextRequest) {
  const form = await request.formData();
  const slug = String(form.get("slug") ?? "").trim();

  if (!slug) {
    return seeOther("/favourites?error=empty");
  }

  const country = bySlug(slug);
  if (!country) {
    return seeOther("/favourites?error=unknown");
  }

  const current = await readFavourites();
  const next = current.includes(country.slug) ? current : [...current, country.slug];

  const response = seeOther(`/favourites?saved=${country.slug}`);
  response.cookies.set(FAVOURITES_COOKIE, next.join(","), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 30,
  });
  return response;
}
