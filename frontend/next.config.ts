import type { NextConfig } from "next";

// Proxy /api/* to the backend so the browser makes same-origin requests
// (no CORS). Override the target with CONSENTINEL_API_URL when the backend
// runs elsewhere (e.g. the Docker stack on :8080).
const apiTarget = process.env.CONSENTINEL_API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiTarget}/:path*` }];
  },
};

export default nextConfig;
