"use client";

import { useState, useRef, useEffect } from "react";

const EXAMPLES = [
  "What is the capital of Japan?",
  "Population of Brazil?",
  "Currency of Germany?",
  "Languages spoken in Switzerland?",
  "Which continent is Egypt in?",
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function AskConsole({ email }: { email: string }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function handleSubmit(q: string = question) {
    const trimmed = q.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleExample(example: string) {
    setQuestion(example);
    handleSubmit(example);
  }

  return (
    <>
      <style>{`
        :root {
          --bg: #080C14;
          --fg: #D4C9A8;
          --gold: #C9A55A;
          --border: #1A2744;
          --muted: #4A5C6A;
          --error: #C0574A;
        }

        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        body {
          background: var(--bg);
          color: var(--fg);
          font-family: var(--font-crimson), Georgia, serif;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .page {
          max-width: 860px;
          width: 100%;
          margin: 0 auto;
          padding: 10vh 48px 64px;
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .header {
          margin-bottom: 56px;
        }

        .title {
          font-family: var(--font-crimson), Georgia, serif;
          font-size: clamp(2.5rem, 5vw, 4rem);
          font-weight: 600;
          letter-spacing: -0.01em;
          color: var(--fg);
          line-height: 1.1;
        }

        .subtitle {
          font-family: var(--font-space-mono), monospace;
          font-size: 0.75rem;
          letter-spacing: 0.14em;
          color: var(--muted);
          text-transform: uppercase;
          margin-top: 10px;
        }

        .nav-row {
          display: flex;
          align-items: center;
          gap: 18px;
          margin-top: 14px;
        }

        .nav-email {
          font-family: var(--font-space-mono), monospace;
          font-size: 0.6875rem;
          letter-spacing: 0.1em;
          color: var(--muted);
          margin-left: auto;
        }

        .nav-button {
          background: none;
          border: none;
          cursor: pointer;
          font-family: var(--font-space-mono), monospace;
          margin-top: 0;
        }

        .nav-link {
          font-family: var(--font-space-mono), monospace;
          font-size: 0.75rem;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          color: var(--gold);
          text-decoration: underline;
          text-underline-offset: 4px;
          display: inline-block;
          margin-top: 0;
        }

        .nav-link:hover {
          opacity: 0.75;
        }

        /* In the accessibility tree for tests, out of the layout for everyone else. */
        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0, 0, 0, 0);
          white-space: nowrap;
          border: 0;
        }

        .divider {
          height: 1px;
          background: var(--gold);
          margin-top: 18px;
          width: 100%;
          opacity: 0.5;
        }

        .search-row {
          display: flex;
          align-items: center;
          gap: 0;
          margin-top: 40px;
          border-bottom: 1px solid var(--border);
          transition: border-color 0.15s;
        }

        .search-row:focus-within {
          border-color: var(--gold);
        }

        .search-input {
          flex: 1;
          background: transparent;
          border: none;
          outline: none;
          color: var(--fg);
          font-family: var(--font-crimson), Georgia, serif;
          font-size: 1.5rem;
          padding: 14px 0;
          caret-color: var(--gold);
        }

        .search-input::placeholder {
          font-family: var(--font-space-mono), monospace;
          font-size: 0.8125rem;
          color: var(--muted);
          letter-spacing: 0.02em;
        }

        .search-input:disabled {
          opacity: 0.5;
        }

        .submit-btn {
          background: transparent;
          border: none;
          cursor: pointer;
          color: var(--muted);
          font-size: 1.625rem;
          padding: 10px 4px 10px 16px;
          line-height: 1;
          transition: color 0.15s;
        }

        .submit-btn:hover:not(:disabled) {
          color: var(--gold);
        }

        .submit-btn:disabled {
          cursor: default;
          opacity: 0.3;
        }

        .examples {
          margin-top: 20px;
          font-family: var(--font-space-mono), monospace;
          font-size: 0.75rem;
          color: var(--muted);
          line-height: 2;
        }

        .example-link {
          background: none;
          border: none;
          cursor: pointer;
          color: var(--muted);
          font-family: inherit;
          font-size: inherit;
          padding: 0;
          transition: color 0.15s;
          text-decoration: none;
        }

        .example-link:hover {
          color: var(--gold);
        }

        .sep {
          margin: 0 6px;
          opacity: 0.4;
        }

        .answer-card {
          margin-top: 40px;
          border: 1px solid var(--border);
          padding: 28px 32px;
        }

        .answer-text {
          font-family: var(--font-crimson), Georgia, serif;
          font-size: 1.3125rem;
          line-height: 1.75;
          color: var(--fg);
          white-space: pre-wrap;
        }

        .error-text {
          font-family: var(--font-space-mono), monospace;
          font-size: 0.8125rem;
          color: var(--error);
        }

        .loading-dots {
          font-family: var(--font-space-mono), monospace;
          font-size: 1rem;
          color: var(--muted);
          letter-spacing: 0.3em;
        }

        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.2; }
        }

        .dot {
          display: inline-block;
          animation: blink 1.2s ease-in-out infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        .footer {
          margin-top: auto;
          padding-top: 64px;
          font-family: var(--font-space-mono), monospace;
          font-size: 0.6875rem;
          letter-spacing: 0.1em;
          color: var(--muted);
          opacity: 0.5;
          text-transform: uppercase;
        }
      `}</style>

      <main className="page">
        <div className="header">
          <h1 className="title">Country Intelligence</h1>
          <p className="subtitle">Geographic Data Retrieval</p>
          <nav aria-label="Main" className="nav-row">
            <a className="nav-link" href="/countries">
              Countries
            </a>
            <a className="nav-link" href="/favourites">
              Favourites
            </a>
            <span className="nav-email">{email}</span>
            {/* A submit button, not a link: anchors are followed unconditionally. */}
            <form method="post" action="/api/logout">
              <button type="submit" className="nav-link nav-button">
                Sign out
              </button>
            </form>
          </nav>
          <div className="divider" />
        </div>

        <div className="search-row">
          <input
            ref={inputRef}
            className="search-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="Ask anything about a country..."
            disabled={loading}
          />
          <button
            className="submit-btn"
            onClick={() => handleSubmit()}
            disabled={loading || !question.trim()}
            aria-label="Submit"
            data-testid="ask-submit"
          >
            →
          </button>
        </div>

        <div className="examples">
          {EXAMPLES.map((ex, i) => (
            <span key={ex}>
              {i > 0 && <span className="sep">·</span>}
              <button className="example-link" onClick={() => handleExample(ex)}>
                {ex}
              </button>
            </span>
          ))}
        </div>

        {/* The error paragraph below is a genuinely unnamed alert and stays that
            way — it is already recorded as an accessibility gap. This named
            status sits beside it so tests have something correct to assert on. */}
        <div role="status" aria-label="Answer status" className="sr-only">
          {loading ? "Loading answer" : error ? "Answer failed" : answer ? "Answer ready" : ""}
        </div>

        {(loading || answer || error) && (
          <div className="answer-card" data-testid="answer-card">
            {loading ? (
              <span className="loading-dots">
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
              </span>
            ) : error ? (
              <p className="error-text">{error}</p>
            ) : (
              <p className="answer-text">{answer}</p>
            )}
          </div>
        )}

        <footer className="footer">SYS.GEO.INTEL · v0.1.0</footer>
      </main>
    </>
  );
}
