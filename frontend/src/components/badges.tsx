import { cn } from "@/lib/cn";
import { confidencePercent, piiBadgeClass, piiLabel } from "@/lib/pii";
import type { PIICategory, RequestStatus } from "@/lib/types";

import { Badge } from "./ui";

export function PiiBadge({ category, confidence }: { category: PIICategory; confidence?: number }) {
  return (
    <Badge className={piiBadgeClass(category)}>
      {piiLabel(category)}
      {category !== "none" && confidence !== undefined ? ` · ${confidencePercent(confidence)}` : ""}
    </Badge>
  );
}

const STATUS_CLASS: Record<RequestStatus, string> = {
  pending: "bg-muted text-muted-foreground",
  approved: "bg-accent/10 text-accent",
  rejected: "bg-destructive/10 text-destructive",
  completed: "bg-[color:var(--color-success)]/10 text-[color:var(--color-success)]",
};

export function StatusBadge({ status }: { status: RequestStatus }) {
  return <Badge className={cn(STATUS_CLASS[status])}>{status}</Badge>;
}
