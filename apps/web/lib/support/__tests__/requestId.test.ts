import { afterEach, describe, expect, it, vi } from "vitest";

import { newRequestId } from "@/lib/support/requestId";

const V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

describe("newRequestId", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("uses crypto.randomUUID when available", () => {
    vi.stubGlobal("crypto", { randomUUID: () => "11111111-2222-4333-8444-555555555555" });
    expect(newRequestId()).toBe("11111111-2222-4333-8444-555555555555");
  });

  it("builds a v4 UUID from getRandomValues in insecure contexts", () => {
    vi.stubGlobal("crypto", { getRandomValues: (a: Uint8Array) => a.fill(0xff) });
    const id = newRequestId();
    expect(id).toHaveLength(36);
    expect(id).toMatch(V4);
    expect(id[14]).toBe("4");
  });

  it("produces different ids with the real generator fallback", () => {
    const real = globalThis.crypto;
    vi.stubGlobal("crypto", { getRandomValues: real.getRandomValues.bind(real) });
    const a = newRequestId();
    const b = newRequestId();
    expect(a).toMatch(V4);
    expect(a).not.toBe(b);
  });
});
