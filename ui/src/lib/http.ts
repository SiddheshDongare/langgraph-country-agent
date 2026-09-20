import { NextResponse } from "next/server";

/**
 * A relative Location header, which the browser resolves against the URL it
 * actually asked for.
 *
 * Building an absolute URL from request.url instead yields Netlify's
 * per-deploy hostname (6aaf…--site.netlify.app) rather than the primary
 * domain. That is a different origin: the session cookie would be set on the
 * wrong host, and the crawler — which only follows same-origin links — would
 * drop everything after the redirect.
 */
export function seeOther(path: string): NextResponse {
  return new NextResponse(null, { status: 303, headers: { Location: path } });
}
