"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";
import { PRINCIPALS, useRole } from "@/lib/role-context";
import type { Role } from "@/lib/types";

import { Select } from "./ui";

const NAV = [
  { href: "/", label: "Datasets" },
  { href: "/requests", label: "Requests" },
];

const ROLE_LABELS: Record<Role, string> = {
  data_owner: "Data owner (alice)",
  data_steward: "Data steward (sam)",
  data_subject: "Data subject (jens)",
  admin: "Admin (root)",
};

export function Header() {
  const pathname = usePathname();
  const { principal, setRole } = useRole();

  return (
    <header className="border-b border-border">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-mono text-sm font-semibold">
            ▮ Consentinel
          </Link>
          <nav className="flex gap-4 text-sm">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "text-muted-foreground transition-colors hover:text-foreground",
                  pathname === item.href && "font-medium text-foreground",
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          Acting as
          <Select
            value={principal.role}
            onChange={(e) => setRole(e.target.value as Role)}
            aria-label="Active role"
          >
            {(Object.keys(PRINCIPALS) as Role[]).map((role) => (
              <option key={role} value={role}>
                {ROLE_LABELS[role]}
              </option>
            ))}
          </Select>
        </label>
      </div>
    </header>
  );
}
