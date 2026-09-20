import crypto from "node:crypto";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export const SESSION_COOKIE = "qa_session";

/**
 * Session is an HMAC of the signed-in email keyed on DEMO_PASSWORD, so the
 * cookie cannot be forged by hand. Nothing sensitive sits behind it — there is
 * no revocation list and no refresh.
 * ponytail: single static key, 8h expiry; if this ever guards real data it
 * needs its own secret and rotation.
 */
function secret(): string | null {
  return process.env.DEMO_PASSWORD || null;
}

function mac(value: string, key: string): string {
  return crypto.createHmac("sha256", key).update(value).digest("base64url");
}

export function safeEqual(a: string, b: string): boolean {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

export function sign(email: string): string {
  const key = secret();
  if (!key) throw new Error("DEMO_PASSWORD is not set");
  return `${Buffer.from(email).toString("base64url")}.${mac(email, key)}`;
}

/** Returns the email, or null. Fails closed when DEMO_PASSWORD is missing. */
export function verify(token: string | undefined): string | null {
  const key = secret();
  if (!key || !token) return null;
  const [encoded, signature] = token.split(".");
  if (!encoded || !signature) return null;
  const email = Buffer.from(encoded, "base64url").toString();
  return safeEqual(signature, mac(email, key)) ? email : null;
}

export async function getSession(): Promise<string | null> {
  const store = await cookies();
  return verify(store.get(SESSION_COOKIE)?.value);
}

export async function requireSession(): Promise<string> {
  const email = await getSession();
  if (!email) redirect("/login");
  return email;
}
