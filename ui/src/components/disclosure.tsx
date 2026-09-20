"use client";

import { useId, useState } from "react";

/**
 * The crawler clicks exactly three things: [aria-expanded], [aria-haspopup] and
 * [role=tab]. A plain button that opens a panel is never opened, so that state
 * is never recorded — hence the real aria-expanded attribute here rather than
 * <details>/<summary>, whose expanded state lives only in the accessibility
 * tree and so does not match the attribute selector.
 *
 * Keep `label` clear of the destructive-word denylist (delete, remove, reset,
 * cancel, …) or the control is skipped outright.
 */
export function Disclosure({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const panelId = useId();

  return (
    <div className="mb-4">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((value) => !value)}
        className="border px-3 py-2 font-medium"
      >
        {label}
      </button>
      <div id={panelId} hidden={!open} className="mt-2 border p-3">
        {children}
      </div>
    </div>
  );
}
