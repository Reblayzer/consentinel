import type { PIICategory } from "./types";

const LABELS: Record<PIICategory, string> = {
  none: "No PII",
  name: "Name",
  email: "Email",
  phone: "Phone",
  national_id: "National ID",
  address: "Address",
  date_of_birth: "Date of birth",
  ip_address: "IP address",
  credit_card: "Credit card",
};

export function piiLabel(category: PIICategory): string {
  return LABELS[category] ?? category;
}

export function isPersonalData(category: PIICategory): boolean {
  return category !== "none";
}

export function confidencePercent(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/** Tailwind classes for a PII badge, escalating colour by sensitivity. */
export function piiBadgeClass(category: PIICategory): string {
  if (category === "none") return "bg-muted text-muted-foreground";
  // Special-category / high-risk identifiers get the destructive colour.
  if (category === "national_id" || category === "credit_card") {
    return "bg-destructive/10 text-destructive";
  }
  return "bg-accent/10 text-accent";
}
