import { afterEach, describe, expect, it, vi } from "vitest";

import { api, ApiError } from "@/lib/api";
import type { Principal } from "@/lib/types";

const owner: Principal = { actor: "alice", role: "data_owner" };

function mockFetch(status: number, body: unknown) {
  const fn = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: "STATUS",
    json: async () => body,
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("attaches auth headers and JSON body when registering a dataset", async () => {
    const fetchMock = mockFetch(201, { id: 1 });
    await api.registerDataset(
      { name: "d", owner: "o", source_system: "s", fields: [] },
      owner,
    );

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/datasets");
    expect(init.method).toBe("POST");
    expect(init.headers["X-Actor"]).toBe("alice");
    expect(init.headers["X-Role"]).toBe("data_owner");
    expect(JSON.parse(init.body)).toMatchObject({ name: "d" });
  });

  it("appends a status filter to the requests query", async () => {
    const fetchMock = mockFetch(200, []);
    await api.listRequests("pending");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/requests?status=pending");
  });

  it("omits the body when completing a request", async () => {
    const fetchMock = mockFetch(200, { id: 1 });
    await api.decideRequest(1, "complete", owner);
    expect(fetchMock.mock.calls[0][1].body).toBeUndefined();
  });

  it("throws ApiError carrying the backend detail message", async () => {
    mockFetch(403, { detail: "role 'data_subject' is not permitted for this action" });
    await expect(api.listAudit({ actor: "x", role: "data_subject" })).rejects.toBeInstanceOf(
      ApiError,
    );
  });
});
