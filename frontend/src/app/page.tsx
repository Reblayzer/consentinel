"use client";

import Link from "next/link";

import { PiiBadge } from "@/components/badges";
import { Button, Card } from "@/components/ui";
import { api } from "@/lib/api";
import { useAsync } from "@/lib/use-async";

export default function DatasetsPage() {
  const { data: datasets, error, loading } = useAsync(() => api.listDatasets());

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-xl font-semibold">Datasets</h1>
          <p className="text-sm text-muted-foreground">
            Registered manifests, with personal data discovered automatically.
          </p>
        </div>
        <Link href="/datasets/new">
          <Button>+ Register dataset</Button>
        </Link>
      </div>

      {loading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {error && (
        <Card className="border-destructive/30">
          <p className="text-sm text-destructive">
            Could not load datasets: {error}. Is the API running on{" "}
            <code className="font-mono">localhost:8000</code>?
          </p>
        </Card>
      )}

      {datasets && datasets.length === 0 && (
        <Card>
          <p className="text-sm text-muted-foreground">
            No datasets yet. Register one to see automatic PII classification in action.
          </p>
        </Card>
      )}

      <div className="space-y-4">
        {datasets?.map((dataset) => (
          <Card key={dataset.id}>
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-mono text-sm font-semibold">{dataset.name}</h2>
                <p className="text-xs text-muted-foreground">
                  {dataset.owner} · {dataset.source_system}
                </p>
              </div>
              {dataset.contains_personal_data ? (
                <span className="text-xs font-medium text-destructive">contains personal data</span>
              ) : (
                <span className="text-xs text-muted-foreground">no personal data</span>
              )}
            </div>

            {dataset.fields.length > 0 && (
              <ul className="mt-4 space-y-1.5">
                {dataset.fields.map((field) => (
                  <li key={field.id} className="flex items-center gap-3 text-sm">
                    <span className="w-40 shrink-0 font-mono text-xs">{field.name}</span>
                    <PiiBadge category={field.pii_category} confidence={field.confidence} />
                    <span className="truncate text-xs text-muted-foreground">{field.rationale}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
