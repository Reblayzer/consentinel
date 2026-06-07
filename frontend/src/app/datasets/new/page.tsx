"use client";

import Link from "next/link";
import { useState } from "react";

import { PiiBadge } from "@/components/badges";
import { Button, Card, Input, Label, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { useRole } from "@/lib/role-context";
import type { Dataset } from "@/lib/types";

interface FieldRow {
  name: string;
  samples: string; // comma-separated, parsed on submit
}

const STARTER_ROWS: FieldRow[] = [
  { name: "email", samples: "a@example.dk, b@example.dk" },
  { name: "cpr", samples: "010203-1234" },
  { name: "order_total", samples: "12.50, 9.99" },
];

export default function NewDatasetPage() {
  const { principal } = useRole();
  const [name, setName] = useState("crm.customers");
  const [owner, setOwner] = useState("marketing-data-team");
  const [sourceSystem, setSourceSystem] = useState("snowflake");
  const [description, setDescription] = useState("");
  const [rows, setRows] = useState<FieldRow[]>(STARTER_ROWS);
  const [result, setResult] = useState<Dataset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function updateRow(index: number, patch: Partial<FieldRow>) {
    setRows((current) => current.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function addRow() {
    setRows((current) => [...current, { name: "", samples: "" }]);
  }

  function removeRow(index: number) {
    setRows((current) => current.filter((_, i) => i !== index));
  }

  async function submit() {
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const dataset = await api.registerDataset(
        {
          name,
          owner,
          source_system: sourceSystem,
          description,
          fields: rows
            .filter((row) => row.name.trim())
            .map((row) => ({
              name: row.name.trim(),
              sample_values: row.samples
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean),
            })),
        },
        principal,
      );
      setResult(dataset);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
          ← Datasets
        </Link>
        <h1 className="mt-2 text-xl font-semibold">Register a dataset</h1>
        <p className="text-sm text-muted-foreground">
          Requires the <code className="font-mono">data_owner</code> role (switch role in the
          header). Each column is classified for personal data on submit.
        </p>
      </div>

      <Card className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="owner">Owner</Label>
            <Input id="owner" value={owner} onChange={(e) => setOwner(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="source">Source system</Label>
            <Input
              id="source"
              value={sourceSystem}
              onChange={(e) => setSourceSystem(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="desc">Description</Label>
            <Input id="desc" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
        </div>

        <div>
          <Label>Columns (name + sample values)</Label>
          <div className="space-y-2">
            {rows.map((row, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  placeholder="column name"
                  value={row.name}
                  onChange={(e) => updateRow(index, { name: e.target.value })}
                  className="w-48"
                />
                <Textarea
                  placeholder="comma-separated sample values"
                  value={row.samples}
                  onChange={(e) => updateRow(index, { samples: e.target.value })}
                  rows={1}
                />
                <Button variant="ghost" onClick={() => removeRow(index)} aria-label="Remove column">
                  ✕
                </Button>
              </div>
            ))}
          </div>
          <Button variant="secondary" className="mt-2" onClick={addRow}>
            + Add column
          </Button>
        </div>

        <Button onClick={submit} disabled={submitting}>
          {submitting ? "Classifying…" : "Register & classify"}
        </Button>

        {error && <p className="text-sm text-destructive">Error: {error}</p>}
      </Card>

      {result && (
        <Card className="space-y-3">
          <h2 className="font-medium">
            Registered <span className="font-mono">{result.name}</span>: classification
          </h2>
          <ul className="space-y-1.5">
            {result.fields.map((field) => (
              <li key={field.id} className="flex items-center gap-3 text-sm">
                <span className="w-40 shrink-0 font-mono text-xs">{field.name}</span>
                <PiiBadge category={field.pii_category} confidence={field.confidence} />
                <span className="text-xs text-muted-foreground">{field.rationale}</span>
              </li>
            ))}
          </ul>
          <Link href="/" className="text-sm text-accent hover:underline">
            View all datasets →
          </Link>
        </Card>
      )}
    </div>
  );
}
