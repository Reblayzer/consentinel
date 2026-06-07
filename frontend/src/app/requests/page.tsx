"use client";

import { useState } from "react";

import { StatusBadge } from "@/components/badges";
import { Button, Card, Input, Label, Select, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { useRole } from "@/lib/role-context";
import type { ComplianceRequest, RequestType } from "@/lib/types";
import { useAsync } from "@/lib/use-async";

export default function RequestsPage() {
  const { principal } = useRole();
  const canDecide = principal.role === "data_steward" || principal.role === "admin";

  const { data: requests, error, loading, reload } = useAsync(() => api.listRequests());

  const [requestType, setRequestType] = useState<RequestType>("erasure");
  const [subjectRef, setSubjectRef] = useState("jens@example.dk");
  const [reason, setReason] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);

  async function file() {
    setActionError(null);
    try {
      await api.fileRequest({ request_type: requestType, subject_ref: subjectRef, reason }, principal);
      setReason("");
      reload();
    } catch (e: unknown) {
      setActionError(e instanceof Error ? e.message : String(e));
    }
  }

  async function decide(
    request: ComplianceRequest,
    action: "approve" | "reject" | "complete",
  ) {
    setActionError(null);
    try {
      await api.decideRequest(request.id, action, principal);
      reload();
    } catch (e: unknown) {
      setActionError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Compliance requests</h1>
        <p className="text-sm text-muted-foreground">
          Right-to-be-forgotten and access requests, with a stewarded approval workflow.
        </p>
      </div>

      <Card className="space-y-4">
        <h2 className="font-medium">File a request</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label htmlFor="type">Type</Label>
            <Select
              id="type"
              value={requestType}
              onChange={(e) => setRequestType(e.target.value as RequestType)}
              className="w-full"
            >
              <option value="erasure">Erasure (right to be forgotten)</option>
              <option value="access">Access (right of access)</option>
            </Select>
          </div>
          <div className="col-span-2">
            <Label htmlFor="subject">Subject reference</Label>
            <Input id="subject" value={subjectRef} onChange={(e) => setSubjectRef(e.target.value)} />
          </div>
        </div>
        <div>
          <Label htmlFor="reason">Reason (optional)</Label>
          <Textarea id="reason" value={reason} onChange={(e) => setReason(e.target.value)} rows={2} />
        </div>
        <Button onClick={file}>File request as {principal.role}</Button>
      </Card>

      {actionError && <p className="text-sm text-destructive">Error: {actionError}</p>}
      {loading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {error && <p className="text-sm text-destructive">Could not load requests: {error}</p>}

      <div className="space-y-3">
        {requests?.map((request) => (
          <Card key={request.id}>
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm">#{request.id}</span>
                  <span className="text-sm font-medium">{request.request_type}</span>
                  <StatusBadge status={request.status} />
                </div>
                <p className="text-xs text-muted-foreground">
                  subject <span className="font-mono">{request.subject_ref}</span> · filed by{" "}
                  {request.requested_by}
                  {request.decided_by && ` · decided by ${request.decided_by}`}
                </p>
              </div>

              {canDecide && (
                <div className="flex gap-2">
                  {request.status === "pending" && (
                    <>
                      <Button onClick={() => decide(request, "approve")}>Approve</Button>
                      <Button variant="destructive" onClick={() => decide(request, "reject")}>
                        Reject
                      </Button>
                    </>
                  )}
                  {request.status === "approved" && (
                    <Button onClick={() => decide(request, "complete")}>Mark complete</Button>
                  )}
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
