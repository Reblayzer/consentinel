"use client";

import { createContext, useContext, useEffect, useState } from "react";

import type { Principal, Role } from "./types";

// Demo principals — one per role. Real auth would derive these from a token;
// here a switcher lets a reviewer experience the app from each perspective.
export const PRINCIPALS: Record<Role, Principal> = {
  data_owner: { actor: "alice", role: "data_owner" },
  data_steward: { actor: "sam", role: "data_steward" },
  data_subject: { actor: "jens", role: "data_subject" },
  admin: { actor: "root", role: "admin" },
};

const STORAGE_KEY = "consentinel-role";

interface RoleContextValue {
  principal: Principal;
  setRole: (role: Role) => void;
}

const RoleContext = createContext<RoleContextValue | null>(null);

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [principal, setPrincipal] = useState<Principal>(PRINCIPALS.data_owner);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Role | null;
    if (stored && PRINCIPALS[stored]) setPrincipal(PRINCIPALS[stored]);
  }, []);

  function setRole(role: Role) {
    setPrincipal(PRINCIPALS[role]);
    localStorage.setItem(STORAGE_KEY, role);
  }

  return <RoleContext.Provider value={{ principal, setRole }}>{children}</RoleContext.Provider>;
}

export function useRole(): RoleContextValue {
  const context = useContext(RoleContext);
  if (!context) throw new Error("useRole must be used within a RoleProvider");
  return context;
}
