import { requireSession } from "@/lib/session";
import { AskConsole } from "@/components/ask-console";

/**
 * The /ask demo sits behind the login like everything else. It keeps its own
 * dark theme and its own nav rather than joining the (secure) route group,
 * whose white app shell would be unreadable over this page's background.
 */
export default async function Home() {
  const email = await requireSession();
  return <AskConsole email={email} />;
}
