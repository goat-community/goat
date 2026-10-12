import type { NextFetchEvent } from "next/server";
import { NextRequest, NextResponse } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { withAuth } from "@/middlewares/withAuth";

const next = vi.fn(async () => NextResponse.next());
const middleware = withAuth(next);

function run(path: string) {
  return middleware(new NextRequest(`http://goat.test${path}`), {} as NextFetchEvent);
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  next.mockClear();
});

describe("withAuth fail-closed", () => {
  it("rejects a protected path when auth is on and NEXTAUTH_SECRET is missing", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.stubEnv("AUTH", "true");
    vi.stubEnv("NEXTAUTH_URL", "http://goat.test");
    vi.stubEnv("NEXTAUTH_SECRET", "");
    const res = await run("/home");
    expect(res?.status).toBe(500);
    expect(await res?.text()).toBe(
      "Authentication is enabled but NEXTAUTH_URL / NEXTAUTH_SECRET are not set"
    );
    expect(next).not.toHaveBeenCalled();
  });

  it("rejects a protected path when auth is on and NEXTAUTH_URL is missing", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.stubEnv("AUTH", "true");
    vi.stubEnv("NEXTAUTH_URL", "");
    vi.stubEnv("NEXTAUTH_SECRET", "secret");
    const res = await run("/projects/abc");
    expect(res?.status).toBe(500);
    expect(next).not.toHaveBeenCalled();
  });

  it("rejects a protected path when AUTH is unset (auth on by default)", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.stubEnv("AUTH", "");
    vi.stubEnv("NEXTAUTH_URL", "");
    vi.stubEnv("NEXTAUTH_SECRET", "");
    const res = await run("/map/abc");
    expect(res?.status).toBe(500);
    expect(next).not.toHaveBeenCalled();
  });

  it("still serves public paths", async () => {
    vi.stubEnv("AUTH", "true");
    vi.stubEnv("NEXTAUTH_URL", "");
    vi.stubEnv("NEXTAUTH_SECRET", "");
    await run("/map/public/abc");
    expect(next).toHaveBeenCalled();
  });

  it("still serves unprotected paths", async () => {
    vi.stubEnv("AUTH", "true");
    vi.stubEnv("NEXTAUTH_URL", "");
    vi.stubEnv("NEXTAUTH_SECRET", "");
    await run("/auth/login");
    expect(next).toHaveBeenCalled();
  });

  it("passes everything when auth is disabled", async () => {
    vi.stubEnv("AUTH", "false");
    vi.stubEnv("NEXTAUTH_URL", "");
    vi.stubEnv("NEXTAUTH_SECRET", "");
    await run("/home");
    expect(next).toHaveBeenCalled();
  });

  it("redirects to login when configured and the request has no session", async () => {
    vi.stubEnv("AUTH", "true");
    vi.stubEnv("NEXTAUTH_URL", "http://goat.test");
    vi.stubEnv("NEXTAUTH_SECRET", "secret");
    const res = await run("/home?tab=1");
    expect(res?.status).toBe(307);
    const location = new URL(res?.headers.get("location") ?? "");
    expect(location.pathname).toBe("/auth/login");
    expect(location.searchParams.get("callbackUrl")).toBe("/home?tab=1");
    expect(next).not.toHaveBeenCalled();
  });
});
