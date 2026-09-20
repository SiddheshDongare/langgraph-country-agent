import { NextRequest } from "next/server";
import { seeOther } from "@/lib/http";
import { SESSION_COOKIE, safeEqual, sign } from "@/lib/session";

/**
 * A plain HTML form POST, so Enter on the password field and a click on the
 * submit button both work without JavaScript — which is how the crawler signs
 * in. On success the redirect target has no password field anywhere, which is
 * the only signal the crawler uses to judge that login worked.
 */
export async function POST(request: NextRequest) {
  const form = await request.formData();
  const email = String(form.get("email") ?? "").trim();
  const password = String(form.get("password") ?? "");

  const expectedEmail = process.env.DEMO_EMAIL;
  const expectedPassword = process.env.DEMO_PASSWORD;

  // No fallback that accepts anything: the wrong-password path is under test.
  const ok =
    Boolean(expectedEmail && expectedPassword) &&
    email.toLowerCase() === expectedEmail!.trim().toLowerCase() &&
    safeEqual(password, expectedPassword!);

  if (!ok) {
    return seeOther("/login?error=1");
  }

  const response = seeOther("/countries");
  response.cookies.set(SESSION_COOKIE, sign(expectedEmail!), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 8,
  });
  return response;
}
