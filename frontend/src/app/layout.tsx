import type { Metadata } from "next";
import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";

import { Header } from "@/components/header";
import { RoleProvider } from "@/lib/role-context";

import "./globals.css";

export const metadata: Metadata = {
  title: "Consentinel",
  description: "Data-governance & compliance portal",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body>
        <RoleProvider>
          <Header />
          <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
        </RoleProvider>
      </body>
    </html>
  );
}
