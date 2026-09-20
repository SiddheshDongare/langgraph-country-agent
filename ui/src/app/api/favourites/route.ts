import { NextRequest, NextResponse } from "next/server";
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
    return NextResponse.redirect(new URL("/favourites?error=empty", request.url), 303);
  }

  const country = bySlug(slug);
  if (!country) {
    return NextResponse.redirect(new URL("/favourites?error=unknown", request.url), 303);
  }

  const current = await readFavourites();
  const next = current.includes(country.slug) ? current : [...current, country.slug];

  const response = NextResponse.redirect(
    new URL(`/favourites?saved=${country.slug}`, request.url),
    303,
  );
  response.cookies.set(FAVOURITES_COOKIE, next.join(","), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 30,
  });
  return response;
}
