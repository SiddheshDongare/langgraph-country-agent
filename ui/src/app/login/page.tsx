import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { getSession } from "@/lib/session";

export const metadata: Metadata = { title: "Sign in" };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  // Already signed in: never leave a password field on a reachable page.
  if (await getSession()) redirect("/countries");
  const { error } = await searchParams;

  return (
    <main className="mx-auto max-w-sm p-8">
      <h1 className="mb-6 text-2xl font-semibold">Sign in</h1>

      {error ? (
        <p role="alert" className="mb-4 text-red-700">
          Invalid email or password.
        </p>
      ) : null}

      <form method="post" action="/api/login" className="flex flex-col gap-3">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="username"
          required
          className="border p-2"
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="border p-2"
        />

        <button type="submit" className="mt-2 border p-2 font-medium">
          Sign in
        </button>
      </form>
    </main>
  );
}
