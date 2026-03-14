import * as React from "react";
import { cn } from "@/lib/utils";

function Badge({
  className,
  ...props
}: React.ComponentProps<"span">) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium transition-colors cursor-pointer select-none hover:bg-accent hover:text-accent-foreground",
        className
      )}
      {...props}
    />
  );
}

export { Badge };
