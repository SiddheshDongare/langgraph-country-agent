import { requireSession } from "@/lib/session";

/**
 * Route group, so it adds no URL segment. /login and / sit outside it: the
 * crawler decides a login succeeded purely by the password field being gone,
 * so the signed-in shell must never be able to render one.
 */
export default async function SecureLayout({ children }: { children: React.ReactNode }) {
  const email = await requireSession();

  return (
    <div className="mx-auto max-w-4xl p-8">
      <header className="mb-6 flex items-center gap-4 border-b pb-3">
        <nav aria-label="Main" className="flex gap-4">
          <a href="/countries" className="underline">
            Countries
          </a>
          <a href="/favourites" className="underline">
            Favourites
          </a>
        </nav>
        <span className="ml-auto text-sm">{email}</span>
        {/* A submit button, not a link: anchors are followed unconditionally. */}
        <form method="post" action="/api/logout">
          <button type="submit" className="border px-2 py-1 text-sm">
            Sign out
          </button>
        </form>
      </header>
      {children}
    </div>
  );
}
