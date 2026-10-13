import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const { publicFetcherMock } = vi.hoisted(() => ({ publicFetcherMock: vi.fn() }));
vi.mock("@/lib/api/publicFetcher", () => ({ publicFetcher: publicFetcherMock }));

/** A fresh module per test: the feed URL is read when the module loads, and SWR caches per import. */
const load = async (feedUrl: string) => {
  vi.stubEnv("NEXT_PUBLIC_STATUS_FEED_URL", feedUrl);
  vi.resetModules();
  return {
    ...(await import("@/lib/api/status")),
    useSWR: (await import("swr")).default,
  };
};

describe("useStatusFeed", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    publicFetcherMock.mockReset();
  });

  it("requests nothing while the feed URL is empty", async () => {
    const { useStatusFeed, useSWR } = await load("");
    const { result } = renderHook(() => useStatusFeed());
    // The production build inlines the URL and folds `|| null` away, so SWR gets the empty string itself.
    renderHook(() => useSWR("", publicFetcherMock));
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(publicFetcherMock).not.toHaveBeenCalled();
    expect(result.current.status).toBeUndefined();
  });

  it("loads the feed once a URL is set", async () => {
    publicFetcherMock.mockResolvedValue({
      generatedAt: "2026-09-04T10:00:00.000Z",
      overall: "operational",
      url: "https://status.example.com/goat",
      systems: [],
      incidents: [],
    });
    const { useStatusFeed } = await load("https://status.example.com/goat.json");
    const { result } = renderHook(() => useStatusFeed());
    await waitFor(() => expect(result.current.status?.overall).toBe("operational"));
    expect(publicFetcherMock).toHaveBeenCalledWith("https://status.example.com/goat.json");
  });
});
