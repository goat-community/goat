import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AssistantRequestError } from "@/lib/assistant/errors";
import {
  cancelAssistantRun,
  createAssistantTransport,
  fetchConversation,
  lastUserMessage,
} from "@/lib/assistant/transport";
import type { AssistantMessage } from "@/lib/assistant/types";

const { getSessionMock } = vi.hoisted(() => ({ getSessionMock: vi.fn() }));

vi.mock("@/lib/api/fetcher", () => ({
  getAccessToken: vi.fn(async () => "tok"),
  fetcher: vi.fn(),
  apiRequestAuth: vi.fn(),
}));
vi.mock("@/lib/constants", () => ({ ASSISTANT_BASE_URL: "http://assistant.test" }));
vi.mock("next-auth/react", () => ({ getSession: getSessionMock }));

const user = (id: string, text: string): AssistantMessage => ({
  id,
  role: "user",
  parts: [{ type: "text", text }],
});
const answer = (id: string): AssistantMessage => ({
  id,
  role: "assistant",
  parts: [{ type: "text", text: "ok" }],
});

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  fetchMock = vi.fn(async () => new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);
  getSessionMock.mockReset();
});
afterEach(() => vi.unstubAllGlobals());

const sent = () => {
  const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
  return { url, init, body: JSON.parse(init.body as string) };
};

async function send(
  transport: ReturnType<typeof createAssistantTransport>,
  messages: AssistantMessage[],
  body?: object,
  trigger: "submit-message" | "regenerate-message" = "submit-message"
): Promise<unknown> {
  return transport
    .sendMessages({ trigger, chatId: "c1", messageId: undefined, messages, abortSignal: undefined, body })
    .catch((error: unknown) => error); // a 204 is not a stream; only the request matters here
}

describe("assistant transport", () => {
  it("posts the newest user message, the page context, the language and the refresh token", async () => {
    getSessionMock.mockResolvedValue({ refresh_token: "refresh-1" });
    const transport = createAssistantTransport("c1", { getLocale: () => "de" });
    await send(transport, [user("m1", "old"), answer("a1"), user("m2", "find bike data")], {
      context: { surface: "catalog", q: "rad" },
    });
    const { url, init, body } = sent();
    expect(url).toBe("http://assistant.test/conversations/c1/runs");
    expect(body).toEqual({
      message: { id: "m2", text: "find bike data" },
      context: { surface: "catalog", q: "rad" },
      locale: "de",
      refresh_token: "refresh-1",
    });
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer tok");
  });

  it("sends no refresh token without a session and no context when the page has none", async () => {
    getSessionMock.mockResolvedValue(null);
    await send(createAssistantTransport("c1"), [user("m1", "hi")]);
    expect(sent().body).toEqual({ message: { id: "m1", text: "hi" }, context: null, locale: "en" });
  });

  it("refuses to regenerate and to send without a user message", async () => {
    const regenerated = await send(
      createAssistantTransport("c1"),
      [user("m1", "hi")],
      undefined,
      "regenerate-message"
    );
    expect(regenerated).toBeInstanceOf(Error);
    expect(fetchMock).not.toHaveBeenCalled();
    expect(() => lastUserMessage([])).toThrow("There is no message to send.");
    expect(() => lastUserMessage([answer("a1")])).toThrow("There is no message to send.");
    expect(lastUserMessage([user("u1", "a"), answer("a1")])).toEqual({ id: "u1", text: "a" });
  });

  it("reads the active run id at reconnect time, not when the transport is built", async () => {
    let current: string | null = null;
    const transport = createAssistantTransport("c1", { getActiveRunId: () => current });
    current = "run-7";
    expect(await transport.reconnectToStream({ chatId: "c1" })).toBeNull(); // 204 = no active run
    current = null;
    await transport.reconnectToStream({ chatId: "c1" });
    const urls = fetchMock.mock.calls.map((call) => call[0]);
    expect(urls).toEqual([
      "http://assistant.test/conversations/c1/stream?run_id=run-7",
      "http://assistant.test/conversations/c1/stream",
    ]);
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer tok");
  });

  it("maps the transcript, its access and the active run", async () => {
    const payload = {
      conversation: { id: "c1", project_id: "p1" },
      messages: [{ id: "m1", role: "user", parts: [{ type: "text", text: "hi" }] }],
      active_run_id: "run-7",
      access: "lost",
      project_name: null,
    };
    fetchMock.mockResolvedValue(new Response(JSON.stringify(payload), { status: 200 }));
    expect(await fetchConversation("c1")).toEqual({
      conversation: payload.conversation,
      messages: payload.messages,
      activeRunId: "run-7",
      access: "lost",
      projectName: null,
      // No ratings in the response: none.
      feedback: {},
    });
  });

  it("cancels server side and throws when the server refuses", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 202 }));
    await expect(cancelAssistantRun("c1")).resolves.toBeUndefined();
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://assistant.test/conversations/c1/cancel");
    expect(init.method).toBe("POST");

    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: { code: "conversation_not_found", message: "gone" } }), {
        status: 404,
      })
    );
    const refused = await cancelAssistantRun("c1").catch((error: unknown) => error);
    expect(refused).toBeInstanceOf(AssistantRequestError);
    expect((refused as AssistantRequestError).code).toBe("conversation_not_found");
  });
});
