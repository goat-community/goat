import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  SUPPORT_API_BASE_URL,
  SupportRequestError,
  createSupportTicket,
  downloadSupportAttachment,
  findSupportTicketByRequestId,
  isSupportEnabled,
  postSupportReply,
  rateSupportTicket,
  refreshSupportTickets,
  reopenSupportTicket,
  resolveSupportTicket,
  revalidateSupport,
  revalidateSupportTickets,
  updateSupportFollowers,
  useSupportSummary,
  useSupportTicket,
  useSupportTickets,
} from "@/lib/api/support";

const { apiRequestAuthMock, fetcherMock } = vi.hoisted(() => ({
  apiRequestAuthMock: vi.fn(),
  fetcherMock: vi.fn(),
}));
vi.mock("@/lib/api/fetcher", () => ({ apiRequestAuth: apiRequestAuthMock, fetcher: fetcherMock }));
const { mutateMock } = vi.hoisted(() => ({ mutateMock: vi.fn() }));
vi.mock("swr", () => ({ mutate: mutateMock }));
const { useAuthedSWRMock } = vi.hoisted(() => ({ useAuthedSWRMock: vi.fn() }));
vi.mock("@/lib/api/useAuthedSWR", () => ({ useAuthedSWR: useAuthedSWRMock }));

const SUPPORT_BASE = SUPPORT_API_BASE_URL;
const ok = (body: unknown, status = 201) => new Response(JSON.stringify(body), { status });

describe("support api", () => {
  beforeEach(() => {
    apiRequestAuthMock.mockReset();
    fetcherMock.mockReset();
    useAuthedSWRMock.mockReset();
    mutateMock.mockReset();
  });

  it("sends a new ticket as multipart with files and technical details", async () => {
    apiRequestAuthMock.mockResolvedValue(ok({ ref: "00041", message_id: 901, failed_files: [] }));
    const file = new File(["PNG"], "a.png", { type: "image/png" });
    const result = await createSupportTicket(
      {
        subject: "Heatmap empty",
        description: "Nothing",
        category: "bug",
        impact: "blocking",
        requestId: "req-12345678",
        colleagueIds: ["u-1", "u-2"],
        technical: { Page: "/map/1" },
      },
      [file]
    );
    expect(result.ref).toBe("00041");
    const [url, init] = apiRequestAuthMock.mock.calls[0];
    expect(url).toMatch(/\/api\/v2\/support\/tickets$/);
    expect(init.method).toBe("POST");
    const form = init.body as FormData;
    expect(form.get("subject")).toBe("Heatmap empty");
    expect(form.get("request_id")).toBe("req-12345678");
    expect(form.getAll("colleague_ids")).toEqual(["u-1", "u-2"]);
    expect(JSON.parse(form.get("technical") as string)).toEqual({ Page: "/map/1" });
    expect((form.getAll("files")[0] as File).name).toBe("a.png");
  });

  it("omits impact when there is none", async () => {
    apiRequestAuthMock.mockResolvedValue(ok({ ref: "00042", message_id: null, failed_files: [] }));
    await createSupportTicket(
      {
        subject: "Idea",
        description: "x",
        category: "feature_request",
        impact: null,
        requestId: "req-abcdefgh",
        colleagueIds: [],
        technical: {},
      },
      []
    );
    expect((apiRequestAuthMock.mock.calls[0][1].body as FormData).has("impact")).toBe(false);
  });

  it("turns error responses into SupportRequestError with the API detail", async () => {
    apiRequestAuthMock.mockResolvedValue(
      new Response(JSON.stringify({ detail: "file_too_large" }), { status: 413 })
    );
    await expect(postSupportReply("00031", "hi", [])).rejects.toMatchObject({
      status: 413,
      detail: "file_too_large",
    });
    await expect(postSupportReply("00031", "hi", [])).rejects.toBeInstanceOf(SupportRequestError);
  });

  it("finds a ticket by request id or returns null", async () => {
    fetcherMock.mockResolvedValueOnce([]).mockResolvedValueOnce([{ ref: "00041" }]);
    expect(await findSupportTicketByRequestId("req-1")).toBeNull();
    expect((await findSupportTicketByRequestId("req-1"))?.ref).toBe("00041");
    expect(fetcherMock.mock.calls[0][0][1]).toEqual({ scope: "mine", state: "open", request_id: "req-1" });
  });

  it("reports a validation error list as invalid_request", async () => {
    apiRequestAuthMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: [{ loc: ["body", "subject"], msg: "too short", type: "string_too_short" }],
        }),
        {
          status: 422,
        }
      )
    );
    await expect(postSupportReply("00031", "hi", [])).rejects.toMatchObject({
      status: 422,
      detail: "invalid_request",
    });
  });

  it("uses an empty detail when the error body is not JSON", async () => {
    apiRequestAuthMock.mockResolvedValue(new Response("<html>bad gateway</html>", { status: 502 }));
    await expect(postSupportReply("00031", "hi", [])).rejects.toMatchObject({ status: 502, detail: "" });
  });

  it("maps the fetcher error shape onto SupportRequestError", () => {
    useAuthedSWRMock.mockReturnValue({
      data: undefined,
      error: { status: 403, info: { detail: "Forbidden" } },
      isLoading: false,
      mutate: vi.fn(),
    });
    expect(useSupportTickets("org", "open").error).toMatchObject({ status: 403, detail: "Forbidden" });
    expect(useAuthedSWRMock.mock.calls[0][0]).toEqual([
      expect.stringMatching(/\/api\/v2\/support\/tickets$/),
      { scope: "org", state: "open" },
    ]);

    useAuthedSWRMock.mockReturnValue({
      data: undefined,
      error: { status: 422, info: { detail: [{ loc: [], msg: "x", type: "y" }] } },
      isLoading: false,
      mutate: vi.fn(),
    });
    expect(useSupportTickets("mine", "closed").error).toMatchObject({
      status: 422,
      detail: "invalid_request",
    });
  });

  describe("support feature probe", () => {
    it("is off until something was received, and on 404", () => {
      expect(isSupportEnabled(undefined, undefined)).toBe(false);
      expect(isSupportEnabled(undefined, { status: 404, info: { detail: "Not Found" } })).toBe(false);
    });

    it("is off without a valid session (401/403)", () => {
      expect(isSupportEnabled(undefined, { status: 401, info: { detail: "Unauthorized" } })).toBe(false);
      expect(isSupportEnabled(undefined, { status: 403, info: { detail: "Forbidden" } })).toBe(false);
    });

    it("stays on for a network error without a status", () => {
      expect(isSupportEnabled(undefined, new TypeError("Failed to fetch"))).toBe(true);
      expect(isSupportEnabled(undefined, { status: 0 })).toBe(true);
    });

    it("stays on for data and for server errors such as Odoo being down", () => {
      expect(isSupportEnabled({ needs_reply: 0, unread: 0 }, undefined)).toBe(true);
      expect(isSupportEnabled(undefined, { status: 503, info: { detail: "support_unavailable" } })).toBe(
        true
      );
      expect(isSupportEnabled(undefined, { status: 500 })).toBe(true);
      expect(isSupportEnabled(undefined, new SyntaxError("not json"))).toBe(true);
      // a transient error after a successful poll keeps the last data
      expect(isSupportEnabled({ needs_reply: 1, unread: 0 }, { status: 503 })).toBe(true);
    });

    it("useSupportSummary exposes the flag", () => {
      useAuthedSWRMock.mockReturnValue({
        data: undefined,
        error: { status: 404, info: { detail: "Not Found" } },
      });
      expect(renderHook(() => useSupportSummary()).result.current.enabled).toBe(false);
      useAuthedSWRMock.mockReturnValue({
        data: undefined,
        error: { status: 503, info: { detail: "support_unavailable" } },
      });
      expect(renderHook(() => useSupportSummary()).result.current.enabled).toBe(true);
    });

    it("counts as on while the first answer is on its way, so the entries show at once", () => {
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: undefined, isLoading: true });
      expect(renderHook(() => useSupportSummary()).result.current.enabled).toBe(true);
      // nothing asked yet (logged out): off
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: undefined, isLoading: false });
      expect(renderHook(() => useSupportSummary()).result.current.enabled).toBe(false);
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: undefined, isLoading: true });
      expect(renderHook(() => useSupportSummary({ enabled: false })).result.current.enabled).toBe(false);
    });

    it("never polls: it loads on mount and on focus, and does not retry errors", () => {
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: undefined });
      renderHook(() => useSupportSummary());
      const config = useAuthedSWRMock.mock.calls.at(-1)?.[2];
      expect(config.refreshInterval).toBeUndefined();
      expect(config.revalidateOnFocus).toBe(true);
      expect(config.shouldRetryOnError).toBe(false);
    });
  });

  describe("useSupportSummary options", () => {
    it("skips the request when disabled", () => {
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: undefined });
      const { result } = renderHook(() => useSupportSummary({ enabled: false }));
      expect(useAuthedSWRMock.mock.calls.at(-1)?.[0]).toBeNull();
      expect(result.current.enabled).toBe(false);
      renderHook(() => useSupportSummary());
      expect(useAuthedSWRMock.mock.calls.at(-1)?.[0]).toMatch(/\/api\/v2\/support\/summary$/);
    });

    it("reports a 404 as not configured", () => {
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: { status: 404, info: { detail: "x" } } });
      expect(renderHook(() => useSupportSummary()).result.current.notConfigured).toBe(true);
      useAuthedSWRMock.mockReturnValue({ data: undefined, error: { status: 503, info: {} } });
      expect(renderHook(() => useSupportSummary()).result.current.notConfigured).toBe(false);
    });
  });

  describe("ticket list keys", () => {
    it("useSupportTickets, the refresh and the revalidation all use the same key", async () => {
      useAuthedSWRMock.mockReturnValue({
        data: undefined,
        error: undefined,
        isLoading: true,
        mutate: vi.fn(),
      });
      useSupportTickets("org", "closed");
      const hookKey = useAuthedSWRMock.mock.calls.at(-1)?.[0];
      expect(hookKey).toEqual([`${SUPPORT_BASE}/tickets`, { scope: "org", state: "closed" }]);

      fetcherMock.mockResolvedValue([]);
      mutateMock.mockImplementation((key: unknown) => Promise.resolve(key));
      await refreshSupportTickets("closed");
      expect(mutateMock.mock.calls.at(-1)?.[0]).toEqual([
        `${SUPPORT_BASE}/tickets`,
        { scope: "mine", state: "closed" },
      ]);
      await refreshSupportTickets("open");
      expect(mutateMock.mock.calls.at(-1)?.[0]).toEqual([
        `${SUPPORT_BASE}/tickets`,
        { scope: "mine", state: "open" },
      ]);
      expect(mutateMock.mock.calls.at(-1)?.[2]).toEqual({ revalidate: false });
    });

    it("revalidateSupportTickets targets every list key but neither summary nor detail", async () => {
      await revalidateSupportTickets();
      const filter = mutateMock.mock.calls.at(-1)![0] as (key: unknown) => boolean;
      for (const scope of ["mine", "org"]) {
        for (const state of ["open", "closed"]) {
          expect(filter([`${SUPPORT_BASE}/tickets`, { scope, state }])).toBe(true);
        }
      }
      expect(filter(`${SUPPORT_BASE}/summary`)).toBe(false);
      expect(filter(`${SUPPORT_BASE}/tickets/00031`)).toBe(false);
      expect(filter("/something/else")).toBe(false);
    });

    it("revalidateSupportTickets can leave some lists out", async () => {
      await revalidateSupportTickets((scope) => scope === "org");
      const filter = mutateMock.mock.calls.at(-1)![0] as (key: unknown) => boolean;
      expect(filter([`${SUPPORT_BASE}/tickets`, { scope: "org", state: "open" }])).toBe(true);
      expect(filter([`${SUPPORT_BASE}/tickets`, { scope: "mine", state: "open" }])).toBe(false);
    });

    it("revalidateSupport still covers the summary and the lists", async () => {
      await revalidateSupport();
      const filter = mutateMock.mock.calls.at(-1)![0] as (key: unknown) => boolean;
      expect(filter(`${SUPPORT_BASE}/summary`)).toBe(true);
      expect(filter([`${SUPPORT_BASE}/tickets`, { scope: "mine", state: "open" }])).toBe(true);
    });
  });

  describe("revalidation after writes", () => {
    const matches = () => {
      const filter = mutateMock.mock.calls.at(-1)![0] as (key: unknown) => boolean;
      return {
        summary: filter(`${SUPPORT_BASE}/summary`),
        list: filter([`${SUPPORT_BASE}/tickets`, { scope: "org", state: "closed" }]),
        detail: filter(`${SUPPORT_BASE}/tickets/00031`),
        other: filter("/something/else"),
      };
    };

    it("revalidates the summary and every list, but not details or other keys", async () => {
      apiRequestAuthMock.mockResolvedValue(ok({ ref: "00041", message_id: 1, failed_files: [] }));
      await postSupportReply("00041", "hi", []);
      expect(matches()).toEqual({ summary: true, list: true, detail: false, other: false });
    });

    it.each([
      [
        "create",
        () =>
          createSupportTicket(
            {
              subject: "Heatmap",
              description: "x",
              category: "bug",
              impact: null,
              requestId: "req-12345678",
              colleagueIds: [],
              technical: {},
            },
            []
          ),
        ok({ ref: "1", message_id: null, failed_files: [] }),
      ],
      ["reply", () => postSupportReply("1", "x", []), ok({ ref: "1", message_id: null, failed_files: [] })],
      ["resolve", () => resolveSupportTicket("1"), new Response(null, { status: 204 })],
      ["reopen", () => reopenSupportTicket("1"), new Response(null, { status: 204 })],
      ["followers", () => updateSupportFollowers("1", {}), new Response(null, { status: 204 })],
      ["rating", () => rateSupportTicket("1", "top", ""), new Response(null, { status: 204 })],
    ])("after %s", async (_name, call, response) => {
      apiRequestAuthMock.mockResolvedValue(response);
      await call();
      expect(mutateMock).toHaveBeenCalledTimes(1);
    });

    it("does not revalidate when the write fails", async () => {
      apiRequestAuthMock.mockResolvedValue(new Response("{}", { status: 503 }));
      await expect(resolveSupportTicket("1")).rejects.toBeInstanceOf(SupportRequestError);
      expect(mutateMock).not.toHaveBeenCalled();
    });

    it("revalidates once a timed-out create turns out to have worked", async () => {
      fetcherMock.mockResolvedValue([]);
      await findSupportTicketByRequestId("req-12345678");
      expect(mutateMock).not.toHaveBeenCalled();
      fetcherMock.mockResolvedValue([{ ref: "00041" }]);
      await findSupportTicketByRequestId("req-12345678");
      expect(mutateMock).toHaveBeenCalledTimes(1);
    });
  });

  it("passes a null key when no ticket is selected", () => {
    useAuthedSWRMock.mockReturnValue({
      data: undefined,
      error: undefined,
      isLoading: false,
      mutate: vi.fn(),
    });
    useSupportTicket(undefined);
    expect(useAuthedSWRMock.mock.calls[0][0]).toBeNull();
    useSupportTicket("00031");
    expect(useAuthedSWRMock.mock.calls[1][0]).toMatch(/\/api\/v2\/support\/tickets\/00031$/);
  });

  it("escapes the ref in urls", async () => {
    apiRequestAuthMock.mockResolvedValue(new Response(null, { status: 204 }));
    await updateSupportFollowers("a/b", {});
    expect(apiRequestAuthMock.mock.calls[0][0]).toMatch(/\/tickets\/a%2Fb\/followers$/);
  });

  it("sends followers as a JSON PUT with empty arrays as defaults", async () => {
    apiRequestAuthMock.mockResolvedValue(new Response(null, { status: 204 }));
    await updateSupportFollowers("00031", { add_user_ids: ["u-1"] });
    await updateSupportFollowers("00031", {});
    const [url, init] = apiRequestAuthMock.mock.calls[0];
    expect(url).toMatch(/\/api\/v2\/support\/tickets\/00031\/followers$/);
    expect(init.method).toBe("PUT");
    expect(init.headers).toEqual({ "Content-Type": "application/json" });
    expect(JSON.parse(init.body)).toEqual({ add_user_ids: ["u-1"], remove_contact_ids: [] });
    expect(JSON.parse(apiRequestAuthMock.mock.calls[1][1].body)).toEqual({
      add_user_ids: [],
      remove_contact_ids: [],
    });
  });

  it("sends a rating as a JSON POST", async () => {
    apiRequestAuthMock.mockResolvedValue(new Response(null, { status: 204 }));
    await rateSupportTicket("00031", "top", "thanks");
    const [url, init] = apiRequestAuthMock.mock.calls[0];
    expect(url).toMatch(/\/api\/v2\/support\/tickets\/00031\/rating$/);
    expect(init.method).toBe("POST");
    expect(init.headers).toEqual({ "Content-Type": "application/json" });
    expect(JSON.parse(init.body)).toEqual({ rating: "top", comment: "thanks" });
  });

  it("names the error class and rethrows lookup failures as SupportRequestError", async () => {
    expect(new SupportRequestError(503, "support_unavailable").name).toBe("SupportRequestError");
    fetcherMock.mockRejectedValueOnce(
      Object.assign(new Error("x"), { status: 503, info: { detail: "support_unavailable" } })
    );
    await expect(findSupportTicketByRequestId("req-1")).rejects.toMatchObject({
      name: "SupportRequestError",
      status: 503,
      detail: "support_unavailable",
    });
    fetcherMock.mockRejectedValueOnce(new SyntaxError("not json"));
    await expect(findSupportTicketByRequestId("req-1")).rejects.toBeInstanceOf(SupportRequestError);
  });

  it("downloads an attachment via a temporary link and revokes the URL later", async () => {
    vi.useFakeTimers();
    const originalCreate = URL.createObjectURL;
    const originalRevoke = URL.revokeObjectURL;
    try {
      apiRequestAuthMock.mockResolvedValue(new Response("data", { status: 200 }));
      const createUrl = vi.fn().mockReturnValue("blob:x");
      const revokeUrl = vi.fn();
      URL.createObjectURL = createUrl;
      URL.revokeObjectURL = revokeUrl;
      const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
        this: HTMLAnchorElement
      ) {
        expect(document.body.contains(this)).toBe(true);
        expect(this.download).toBe("a.png");
      });
      await downloadSupportAttachment("00031", { id: 7, name: "a.png", mimetype: "image/png", size: 4 });
      expect(apiRequestAuthMock.mock.calls[0][0]).toMatch(
        /\/api\/v2\/support\/tickets\/00031\/attachments\/7$/
      );
      expect(click).toHaveBeenCalledTimes(1);
      expect(document.querySelector("a[download]")).toBeNull();
      expect(revokeUrl).not.toHaveBeenCalled();
      vi.runAllTimers();
      expect(revokeUrl).toHaveBeenCalledWith("blob:x");
    } finally {
      vi.useRealTimers();
      vi.restoreAllMocks();
      URL.createObjectURL = originalCreate;
      URL.revokeObjectURL = originalRevoke;
    }
  });
});
