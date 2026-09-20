"use client";

import { useId, useState } from "react";

export type Panel = { label: string; content: React.ReactNode };

/**
 * Real role=tablist/tab/tabpanel, because role=tab is one of the three things
 * the crawler clicks. Deliberately client-side state and not links: the value
 * here is several states on one URL, and tabs-as-links would instead spend the
 * ten-page walk budget.
 */
export function Tabs({ panels, label }: { panels: Panel[]; label: string }) {
  const [active, setActive] = useState(0);
  const base = useId();

  return (
    <div className="mb-6">
      <div role="tablist" aria-label={label} className="flex gap-2 border-b">
        {panels.map((panel, index) => (
          <button
            key={panel.label}
            type="button"
            role="tab"
            id={`${base}-tab-${index}`}
            aria-selected={active === index}
            aria-controls={`${base}-panel-${index}`}
            tabIndex={active === index ? 0 : -1}
            onClick={() => setActive(index)}
            className={`px-3 py-2 ${active === index ? "border-b-2 border-black font-semibold" : ""}`}
          >
            {panel.label}
          </button>
        ))}
      </div>

      {panels.map((panel, index) => (
        <div
          key={panel.label}
          role="tabpanel"
          id={`${base}-panel-${index}`}
          aria-labelledby={`${base}-tab-${index}`}
          hidden={active !== index}
          tabIndex={0}
          className="p-3"
        >
          {panel.content}
        </div>
      ))}
    </div>
  );
}
