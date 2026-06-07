import { describe, expect, it } from "vitest";

import { confidencePercent, isPersonalData, piiBadgeClass, piiLabel } from "@/lib/pii";

describe("pii helpers", () => {
  it("labels categories for humans", () => {
    expect(piiLabel("national_id")).toBe("National ID");
    expect(piiLabel("none")).toBe("No PII");
  });

  it("identifies personal data", () => {
    expect(isPersonalData("email")).toBe(true);
    expect(isPersonalData("none")).toBe(false);
  });

  it("formats confidence as a percentage", () => {
    expect(confidencePercent(1)).toBe("100%");
    expect(confidencePercent(0.335)).toBe("34%");
  });

  it("escalates badge colour for high-risk identifiers", () => {
    expect(piiBadgeClass("national_id")).toContain("destructive");
    expect(piiBadgeClass("credit_card")).toContain("destructive");
    expect(piiBadgeClass("email")).toContain("accent");
    expect(piiBadgeClass("none")).toContain("muted");
  });
});
