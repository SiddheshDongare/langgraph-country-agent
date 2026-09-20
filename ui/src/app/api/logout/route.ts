import { seeOther } from "@/lib/http";
import { SESSION_COOKIE } from "@/lib/session";

/**
 * POST only, and the control that calls it is a submit button rather than a
 * link: the crawler follows every anchor it finds, so a sign-out link would
 * end the walk. It never submits a form, so this is unreachable to it.
 */
export async function POST() {
  const response = seeOther("/login");
  response.cookies.delete(SESSION_COOKIE);
  return response;
}
