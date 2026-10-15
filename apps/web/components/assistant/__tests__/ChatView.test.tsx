import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { UIMessageChunk } from "ai";
import { StrictMode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { refreshConversationLists } from "@/lib/assistant/conversations";
import { AssistantRequestError } from "@/lib/assistant/errors";
import {
  getDockState,
  getDraft,
  registerSurface,
  resetAssistantStore,
  saveDraft,
} from "@/lib/assistant/store";

import ChatView, { type ChatViewProps, STOP_GRACE_MS } from "@/components/assistant/ChatView";
import { DockActionsContext } from "@/components/assistant/DockActions";
import {
  FINISH,
  START,
  dockActions,
  gatedStream,
  refusal,
  stream,
  text,
} from "@/components/assistant/__tests__/helpers";

const { sendMessages, reconnectToStream, cancelMock } = vi.hoisted(() => ({
  sendMessages: vi.fn(),
  reconnectToStream: vi.fn(async (_options?: unknown) => null),
  cancelMock: vi.fn(),
}));

vi.mock("@/lib/assistant/transport", () => ({
  createAssistantTransport: vi.fn(() => ({
    sendMessages: (options: unknown) => sendMessages(options),
    reconnectToStream: (options: unknown) => reconnectToStream(options),
  })),
  cancelAssistantRun: cancelMock,
  fetchConversation: vi.fn(),
  createConversation: vi.fn(),
}));
vi.mock("@/lib/assistant/conversations", () => ({ refreshConversationLists: vi.fn() }));
vi.mock("@/lib/api/fetcher", () => ({ getAccessToken: vi.fn(), fetcher: vi.fn(), apiRequestAuth: vi.fn() }));
vi.mock("@/lib/api/projects", () => ({ useProjects: () => ({ projects: { items: [] }, isLoading: false }) }));
vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en" } }),
}));

const actions = dockActions();

function renderChat(props: Partial<ChatViewProps> = {}, { strict = false } = {}) {
  const onReconnect = vi.fn();
  const onBound = vi.fn();
  const onAccessLost = vi.fn();
  const view = (
    <DockActionsContext.Provider value={actions}>
      <ChatView
        conversationId="c1"
        title=""
        projectId={null}
        projectName={null}
        initialMessages={[]}
        activeRunId={null}
        resume={false}
        readOnly={null}
        firstMessage={null}
        onReconnect={onReconnect}
        onBound={onBound}
        onAccessLost={onAccessLost}
        {...props}
      />
    </DockActionsContext.Provider>
  );
  const { unmount } = render(strict ? <StrictMode>{view}</StrictMode> : view);
  return { onReconnect, onBound, onAccessLost, unmount };
}

function type(value: string) {
  fireEvent.change(screen.getByRole("textbox"), { target: { value } });
}

function send(value: string) {
  type(value);
  fireEvent.click(screen.getByRole("button", { name: "assistant_send" }));
}

const queuedItem = () => screen.getByRole("group", { name: "assistant_queued" });

beforeEach(() => {
  window.sessionStorage.clear();
  resetAssistantStore();
  vi.clearAllMocks();
  registerSurface({
    surface: "catalog",
    getContext: () => ({ surface: "catalog", q: "rad", facets: { themes: ["transportation"] } }),
  });
});

describe("ChatView", () => {
  it("sends with the page context and queues, not sends, what is sent while the answer streams", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("Teil")], "hang"));
    renderChat();
    send("Hallo");
    await screen.findByText("Teil");
    const [options] = sendMessages.mock.calls[0] as [
      { body: unknown; messages: { parts: { type: string }[] }[] },
    ];
    expect(options.body).toEqual({
      context: { surface: "catalog", q: "rad", facets: { themes: ["transportation"] } },
    });
    expect(options.messages[0].parts.map((part) => part.type)).toEqual(["text", "data-context"]);
    // Send stays next to Stop; with no text it has nothing to send.
    expect(screen.getByRole("button", { name: "stop" })).toBeTruthy();
    expect((screen.getByRole("button", { name: "assistant_send" }) as HTMLButtonElement).disabled).toBe(true);
    type("noch eine");
    fireEvent.keyDown(screen.getByRole("textbox"), { key: "Enter" });
    expect(sendMessages).toHaveBeenCalledTimes(1);
    expect(within(queuedItem()).getByText("noch eine")).toBeTruthy();
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe("");
  });

  it("records the newest answer known at send time with the pending run", async () => {
    sendMessages.mockResolvedValue(stream([...START], "hang"));
    renderChat({
      initialMessages: [
        { id: "u1", role: "user", parts: [{ type: "text", text: "Erste" }] },
        { id: "a7", role: "assistant", parts: [{ type: "text", text: "Antwort" }] },
        { id: "u2", role: "user", parts: [{ type: "text", text: "Zweite" }] },
      ],
    });
    send("Dritte");
    await waitFor(() => expect(getDockState().pending).toHaveLength(1));
    expect(getDockState().pending[0]).toMatchObject({ conversationId: "c1", knownAnswerId: "a7" });
  });

  it("records no known answer for a conversation without one", async () => {
    sendMessages.mockResolvedValue(stream([...START], "hang"));
    renderChat();
    send("Erste");
    await waitFor(() => expect(getDockState().pending).toHaveLength(1));
    expect(getDockState().pending[0].knownAnswerId).toBeNull();
  });

  it("lets a stopped answer end with the server's own note", async () => {
    let release: (chunks: UIMessageChunk[]) => void = () => undefined;
    sendMessages.mockResolvedValue(
      gatedStream(
        [...START, ...text("Teil")],
        new Promise<UIMessageChunk[]>((resolve) => (release = resolve))
      )
    );
    cancelMock.mockImplementation(async () => {
      // The server cancels the run; its stream ends with the run-status part.
      release([
        { type: "finish-step" },
        { type: "data-run-status", data: { status: "cancelled", error: null, code: null } },
        { type: "abort" },
      ]);
    });
    renderChat();
    send("Hallo");
    await screen.findByText("Teil");
    fireEvent.click(screen.getByRole("button", { name: "stop" }));
    await screen.findByText("assistant_run_cancelled");
    expect(cancelMock).toHaveBeenCalledWith("c1");
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
  });

  it("cancels again once the stream starts when Stop came before the server began the run", async () => {
    let respond: (value: ReadableStream<UIMessageChunk>) => void = () => undefined;
    let release: (chunks: UIMessageChunk[]) => void = () => undefined;
    sendMessages.mockReturnValue(new Promise((resolve) => (respond = resolve)));
    // The first cancel arrives before begin_run: 204, nothing stopped.
    cancelMock.mockResolvedValueOnce(undefined).mockImplementationOnce(async () => {
      release([
        { type: "finish-step" },
        { type: "data-run-status", data: { status: "cancelled", error: null, code: null } },
        { type: "abort" },
      ]);
    });
    renderChat();
    send("Hallo");
    fireEvent.click(await screen.findByRole("button", { name: "stop" }));
    await waitFor(() => expect(cancelMock).toHaveBeenCalledTimes(1));
    respond(
      gatedStream(
        [...START, ...text("Teil")],
        new Promise<UIMessageChunk[]>((resolve) => (release = resolve))
      )
    );
    await screen.findByText("assistant_run_cancelled");
    expect(cancelMock).toHaveBeenCalledTimes(2);
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
  });

  it("cancels once more and drops the connection when the stream does not end in time", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("Teil")], "hang"));
    cancelMock.mockResolvedValue(undefined);
    renderChat();
    send("Hallo");
    await screen.findByText("Teil");
    vi.useFakeTimers();
    try {
      fireEvent.click(screen.getByRole("button", { name: "stop" }));
      await act(async () => {
        await vi.advanceTimersByTimeAsync(STOP_GRACE_MS + 200);
      });
    } finally {
      vi.useRealTimers();
    }
    expect(cancelMock).toHaveBeenCalledTimes(2);
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
  });

  it("sends no late cancel after the chat unmounted during a Stop", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("Teil")], "hang"));
    cancelMock.mockResolvedValue(undefined);
    const { unmount } = renderChat();
    send("Hallo");
    await screen.findByText("Teil");
    vi.useFakeTimers();
    try {
      fireEvent.click(screen.getByRole("button", { name: "stop" }));
      await act(async () => {
        await vi.advanceTimersByTimeAsync(STOP_GRACE_MS / 2);
      });
      expect(cancelMock).toHaveBeenCalledTimes(1);
      unmount();
      await vi.advanceTimersByTimeAsync(STOP_GRACE_MS * 2);
      expect(vi.getTimerCount()).toBe(0);
    } finally {
      vi.useRealTimers();
    }
    expect(cancelMock).toHaveBeenCalledTimes(1);
  });

  it("drops the connection at once when the server cannot be told to stop", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("Teil")], "hang"));
    cancelMock.mockRejectedValue(new AssistantRequestError(404, "conversation_not_found"));
    renderChat();
    send("Hallo");
    await screen.findByText("Teil");
    fireEvent.click(screen.getByRole("button", { name: "stop" }));
    await screen.findByText("assistant_error_conversation_not_found");
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
  });

  it("puts a refused message back into the composer with the reason", async () => {
    sendMessages.mockRejectedValue(refusal(409, { code: "conversation_busy", message: "busy" }));
    renderChat();
    send("Hallo");
    await screen.findByText("assistant_error_conversation_busy");
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe("Hallo");
    expect(screen.queryByText("Hallo", { ignore: "textarea" })).toBeNull();
  });

  it("never drops stored messages when a reconnect is refused", async () => {
    reconnectToStream.mockRejectedValueOnce(refusal(403, { code: "project_access_lost", message: "lost" }));
    const { onAccessLost } = renderChat({
      resume: true,
      activeRunId: "run-1",
      initialMessages: [{ id: "u1", role: "user", parts: [{ type: "text", text: "Gespeichert" }] }],
    });
    await screen.findByText("assistant_error_project_access_lost");
    expect(screen.getByText("Gespeichert")).toBeTruthy();
    expect(onAccessLost).toHaveBeenCalled();
  });

  it("shows a failed answer with its own note, not a second error", async () => {
    sendMessages.mockResolvedValue(
      stream([
        ...START,
        { type: "finish-step" },
        { type: "data-run-status", data: { status: "failed", error: "x", code: "goat_ai_busy" } },
        { type: "error", errorText: "x" },
      ])
    );
    renderChat();
    send("Hallo");
    await screen.findByText("assistant_run_error_goat_ai_busy");
    expect(screen.queryByText("assistant_error_generic")).toBeNull();
  });

  it("shows a failed answer without a known code with the generic note, never the server's English", async () => {
    sendMessages.mockResolvedValue(
      stream([
        ...START,
        { type: "finish-step" },
        {
          type: "data-run-status",
          data: { status: "failed", error: "Model refused the request", code: null },
        },
        { type: "error", errorText: "Model refused the request" },
      ])
    );
    renderChat();
    send("Hallo");
    await screen.findByText("assistant_run_error_unknown");
    expect(screen.queryByText(/Model refused/)).toBeNull();
    expect(screen.queryByText("assistant_error_generic")).toBeNull();
  });

  it("translates a stream error instead of showing its English text", async () => {
    sendMessages.mockResolvedValue(
      stream([...START, { type: "error", errorText: "Upstream provider overloaded" }])
    );
    renderChat();
    send("Hallo");
    await screen.findByText("assistant_error_generic");
    expect(screen.queryByText(/Upstream provider/)).toBeNull();
  });

  it("never shows the English message of a refusal", async () => {
    sendMessages.mockRejectedValue(
      refusal(429, { code: "user_run_limit", message: "Too many runs at once" })
    );
    renderChat();
    send("Hallo");
    await screen.findByText("assistant_error_user_run_limit");
    expect(screen.queryByText(/Too many runs/)).toBeNull();
  });

  it("offers a reconnect after the connection dropped, also when the browser calls it differently", async () => {
    sendMessages.mockResolvedValueOnce(stream([...START, ...text("Hallo")], new TypeError("network error")));
    const { onReconnect } = renderChat();
    send("Hallo?");
    fireEvent.click(await screen.findByRole("button", { name: "assistant_reconnect" }));
    expect(onReconnect).toHaveBeenCalled();
    expect(screen.queryByText("assistant_error_offline")).toBeNull();
    // Safari reports a dropped fetch as "Load failed".
    sendMessages.mockResolvedValueOnce(stream([...START, ...text("Zwei")], new TypeError("Load failed")));
    send("Noch einmal?");
    await screen.findByText("Zwei");
    expect(await screen.findByText("assistant_disconnected")).toBeTruthy();
  });

  it("leaves out the context the user removed", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("ok"), ...FINISH]));
    renderChat();
    const chip = screen.getByText("assistant_chip_filters").closest(".MuiChip-root") as HTMLElement;
    fireEvent.click(chip.querySelector('[data-testid="CancelIcon"]') as Element);
    send("Hallo");
    await screen.findByText("ok");
    const [options] = sendMessages.mock.calls[0] as [{ body: unknown }];
    expect(options.body).toEqual({ context: { surface: "catalog", q: "rad" } });
    // Accepted: the next message carries the whole page context again.
    expect(screen.getAllByText("assistant_chip_filters").length).toBeGreaterThan(0);
  });

  it("keeps the chips as they were when a send is refused", async () => {
    sendMessages.mockRejectedValue(refusal(409, { code: "conversation_busy", message: "busy" }));
    renderChat();
    const chip = screen.getByText("assistant_chip_filters").closest(".MuiChip-root") as HTMLElement;
    fireEvent.click(chip.querySelector('[data-testid="CancelIcon"]') as Element);
    send("Hallo");
    await screen.findByText("assistant_error_conversation_busy");
    expect(screen.queryByText("assistant_chip_filters")).toBeNull();
    expect(screen.getByText("assistant_chip_search")).toBeTruthy();
  });

  it("reports the binding of an unbound conversation sent from a project page", async () => {
    act(() => {
      registerSurface({
        surface: "project.map",
        project: { id: "p1", name: "Eins" },
        getContext: () => ({ surface: "project.map", project_id: "p1" }),
      });
    });
    sendMessages.mockResolvedValue(stream([...START, ...text("ok"), ...FINISH]));
    const { onBound } = renderChat();
    send("Welche Layer?");
    await screen.findByText("ok");
    expect(onBound).toHaveBeenCalledWith("p1", "Eins");
  });

  it("learns the project from a refusal that names it", async () => {
    sendMessages.mockRejectedValue(
      refusal(409, { code: "conversation_bound", message: "x", project_id: "p9" })
    );
    const { onBound } = renderChat();
    send("Hallo");
    await screen.findByText("assistant_error_conversation_bound");
    expect(onBound).toHaveBeenCalledWith("p9", null);
  });

  it("shows a conversation bound to another project read only", () => {
    renderChat({ readOnly: { kind: "elsewhere", projectId: "p1", projectName: "Radnetz" } });
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(screen.getByText("assistant_readonly_elsewhere")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "assistant_open_in_project" }));
    expect(actions.openInProject).toHaveBeenCalledWith("p1");
    fireEvent.click(screen.getByRole("button", { name: "assistant_new_here" }));
    expect(actions.newConversationHere).toHaveBeenCalled();
  });

  it("shows a conversation the user lost access to without a way to continue it", () => {
    renderChat({ readOnly: { kind: "lost" } });
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(screen.getByText("assistant_lost_access")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "assistant_open_in_project" })).toBeNull();
  });

  it("sends the first message of a new conversation once, also under StrictMode", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("ok"), ...FINISH]));
    renderChat({ firstMessage: { text: "Erste Frage", context: null } }, { strict: true });
    await screen.findByText("ok");
    expect(sendMessages).toHaveBeenCalledTimes(1);
    expect(screen.getByText("Erste Frage")).toBeTruthy();
  });
});

describe("ChatView drafts (ruling 22)", () => {
  const removeFilters = () => {
    const chip = screen.getByText("assistant_chip_filters").closest(".MuiChip-root") as HTMLElement;
    fireEvent.click(chip.querySelector('[data-testid="CancelIcon"]') as Element);
  };

  it("keeps the typed text and the removed chips across a remount (expand or collapse)", () => {
    const { unmount } = renderChat();
    removeFilters();
    type("Noch nicht gesendet");
    unmount();
    renderChat();
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe("Noch nicht gesendet");
    expect(screen.queryByText("assistant_chip_filters")).toBeNull();
    expect(screen.getByText("assistant_chip_search")).toBeTruthy();
  });

  it("clears the draft when the send is accepted, and refreshes the history", async () => {
    sendMessages.mockResolvedValue(stream([...START, ...text("ok"), ...FINISH]));
    const { unmount } = renderChat();
    removeFilters();
    send("Hallo");
    await screen.findByText("ok");
    expect(getDraft("c1")).toBeNull();
    expect(refreshConversationLists).toHaveBeenCalled();
    unmount();
    renderChat();
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe("");
    expect(screen.getByText("assistant_chip_filters")).toBeTruthy();
  });

  it("keeps the draft when the send is refused", async () => {
    sendMessages.mockRejectedValue(refusal(409, { code: "conversation_busy", message: "busy" }));
    const { unmount } = renderChat();
    send("Hallo");
    await screen.findByText("assistant_error_conversation_busy");
    expect(getDraft("c1")?.text).toBe("Hallo");
    unmount();
    renderChat();
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe("Hallo");
  });
});

describe("ChatView queue", () => {
  // A reply a test did not use must not answer the next test's send.
  beforeEach(() => {
    sendMessages.mockReset();
    cancelMock.mockReset();
  });

  const START2: UIMessageChunk[] = [{ type: "start", messageId: "a2" }, { type: "start-step" }];
  const FAILED: UIMessageChunk[] = [
    { type: "finish-step" },
    { type: "data-run-status", data: { status: "failed", error: "x", code: "goat_ai_busy" } },
    { type: "error", errorText: "x" },
  ];
  const CANCELLED: UIMessageChunk[] = [
    { type: "finish-step" },
    { type: "data-run-status", data: { status: "cancelled", error: null, code: null } },
    { type: "abort" },
  ];
  const CONTEXT = { surface: "catalog", q: "rad", facets: { themes: ["transportation"] } };

  /** An answer that streams "Teil" and ends with the chunks passed to `end`. */
  function runningAnswer() {
    let release: (chunks: UIMessageChunk[]) => void = () => undefined;
    const body = gatedStream(
      [...START, ...text("Teil")],
      new Promise<UIMessageChunk[]>((resolve) => (release = resolve))
    );
    // A copy: the stream takes its chunks off the array it gets.
    return {
      body,
      /** For a mock the chat calls itself (it is inside React's updates already). */
      release: (chunks: UIMessageChunk[]) => release([...chunks]),
      end: (chunks: UIMessageChunk[]) => act(async () => release([...chunks])),
    };
  }

  /** The text of the user message the `index`th request carried. */
  const sentText = (index: number) => {
    const [options] = sendMessages.mock.calls[index] as [
      { messages: { role: string; parts: { type: string; text?: string }[] }[] },
    ];
    const user = options.messages.filter((message) => message.role === "user").at(-1);
    return user?.parts.find((part) => part.type === "text")?.text;
  };
  const composerText = () => (screen.getByRole("textbox") as HTMLTextAreaElement).value;
  const noQueue = () => expect(screen.queryByRole("group", { name: "assistant_queued" })).toBeNull();

  it("sends the queued message by itself once the answer ended normally, with the page context", async () => {
    const run = runningAnswer();
    sendMessages
      .mockResolvedValueOnce(run.body)
      .mockResolvedValueOnce(stream([...START2, ...text("Zwei"), ...FINISH]));
    renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite Frage");
    expect(within(queuedItem()).getByText("Zweite Frage")).toBeTruthy();
    expect(sendMessages).toHaveBeenCalledTimes(1);
    await run.end(FINISH);
    await screen.findByText("Zwei");
    expect(sendMessages).toHaveBeenCalledTimes(2);
    expect(sentText(1)).toBe("Zweite Frage");
    expect((sendMessages.mock.calls[1] as [{ body: unknown }])[0].body).toEqual({ context: CONTEXT });
    noQueue();
    expect(getDraft("c1")?.queued ?? null).toBeNull();
  });

  it("keeps the queued message when the answer failed", async () => {
    const run = runningAnswer();
    sendMessages.mockResolvedValueOnce(run.body);
    renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite Frage");
    await run.end(FAILED);
    await screen.findByText("assistant_run_error_goat_ai_busy");
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
    expect(within(queuedItem()).getByText("Zweite Frage")).toBeTruthy();
    expect(within(queuedItem()).getByRole("button", { name: "assistant_send_now" })).toBeTruthy();
    expect(sendMessages).toHaveBeenCalledTimes(1);
  });

  it("keeps the queued message when the answer was stopped", async () => {
    const run = runningAnswer();
    sendMessages.mockResolvedValueOnce(run.body);
    cancelMock.mockImplementation(async () => run.release(CANCELLED));
    renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite Frage");
    fireEvent.click(screen.getByRole("button", { name: "stop" }));
    await screen.findByText("assistant_run_cancelled");
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
    // Long enough for the Stop to have settled.
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 200));
    });
    expect(within(queuedItem()).getByText("Zweite Frage")).toBeTruthy();
    expect(sendMessages).toHaveBeenCalledTimes(1);
  });

  it("Send now stops the answer the way Stop does, then sends the queued message", async () => {
    // Time runs, and can be skipped past the Stop's grace period at the end.
    vi.useFakeTimers({ shouldAdvanceTime: true });
    try {
      const run = runningAnswer();
      sendMessages
        .mockResolvedValueOnce(run.body)
        .mockResolvedValueOnce(stream([...START2, ...text("Zwei")], "hang"));
      cancelMock.mockImplementation(async () => run.release(CANCELLED));
      renderChat();
      send("Eins");
      await screen.findByText("Teil");
      send("Zweite Frage");
      fireEvent.click(within(queuedItem()).getByRole("button", { name: "assistant_send_now" }));
      await screen.findByText("Zwei");
      expect(screen.getByText("assistant_run_cancelled")).toBeTruthy();
      expect(sentText(1)).toBe("Zweite Frage");
      noQueue();
      await act(async () => {
        await vi.advanceTimersByTimeAsync(STOP_GRACE_MS + 200);
      });
      // The Stop had ended before the send: no late cancel stops the new run, nor forgets it.
      expect(cancelMock).toHaveBeenCalledTimes(1);
      expect(getDockState().pending).toHaveLength(1);
      expect(screen.getByRole("button", { name: "stop" })).toBeTruthy();
    } finally {
      vi.useRealTimers();
    }
  });

  it("Remove puts the queued text back into the composer, ahead of what was typed since", async () => {
    const run = runningAnswer();
    sendMessages.mockResolvedValueOnce(run.body);
    renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite Frage");
    type("Dritte");
    fireEvent.click(within(queuedItem()).getByRole("button", { name: "remove" }));
    noQueue();
    expect(composerText()).toBe("Zweite Frage\nDritte");
    await run.end(FINISH);
    await waitFor(() => expect(screen.queryByRole("button", { name: "stop" })).toBeNull());
    expect(sendMessages).toHaveBeenCalledTimes(1);
    expect(composerText()).toBe("Zweite Frage\nDritte");
  });

  it("adds a further message to the queued one on a new line", async () => {
    const run = runningAnswer();
    sendMessages
      .mockResolvedValueOnce(run.body)
      .mockResolvedValueOnce(stream([...START2, ...text("Zwei"), ...FINISH]));
    renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite");
    send("Dritte");
    expect(screen.getAllByRole("group", { name: "assistant_queued" })).toHaveLength(1);
    expect(getDraft("c1")?.queued?.text).toBe("Zweite\nDritte");
    await run.end(FINISH);
    await screen.findByText("Zwei");
    expect(sendMessages).toHaveBeenCalledTimes(2);
    expect(sentText(1)).toBe("Zweite\nDritte");
  });

  it("joins and sends at once what is sent while a message is queued and nothing runs", async () => {
    saveDraft("c1", { queued: { text: "Zweite", reason: "assistant_error_conversation_busy" } });
    sendMessages.mockResolvedValueOnce(stream([...START2, ...text("Zwei"), ...FINISH]));
    renderChat();
    expect(within(queuedItem()).getByText("assistant_error_conversation_busy")).toBeTruthy();
    send("Dritte");
    await screen.findByText("Zwei");
    expect(sendMessages).toHaveBeenCalledTimes(1);
    expect(sentText(0)).toBe("Zweite\nDritte");
    noQueue();
  });

  it("keeps the queued message across a remount, and sends it only on request then", async () => {
    sendMessages
      .mockResolvedValueOnce(stream([...START, ...text("Teil")], "hang"))
      .mockResolvedValueOnce(stream([...START2, ...text("Zwei"), ...FINISH]));
    const { unmount } = renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite Frage");
    unmount();
    expect(getDraft("c1")?.queued).toEqual({ text: "Zweite Frage", reason: null });
    renderChat();
    expect(within(queuedItem()).getByText("Zweite Frage")).toBeTruthy();
    // How the answer ended is not known here: nothing goes by itself.
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 20));
    });
    expect(sendMessages).toHaveBeenCalledTimes(1);
    fireEvent.click(within(queuedItem()).getByRole("button", { name: "assistant_send_now" }));
    await screen.findByText("Zwei");
    expect(sentText(1)).toBe("Zweite Frage");
  });

  it("puts a refused queued message back into the queue with the translated reason", async () => {
    const run = runningAnswer();
    sendMessages
      .mockResolvedValueOnce(run.body)
      .mockRejectedValueOnce(refusal(409, { code: "conversation_busy", message: "Conversation is busy" }));
    renderChat();
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite");
    type("Tippe weiter");
    await run.end(FINISH);
    await screen.findByText("assistant_error_conversation_busy");
    expect(sendMessages).toHaveBeenCalledTimes(2);
    expect(within(queuedItem()).getByText("Zweite")).toBeTruthy();
    expect(within(queuedItem()).getByText("assistant_error_conversation_busy")).toBeTruthy();
    // Said once, in the item, and never in the server's English.
    expect(screen.getAllByText("assistant_error_conversation_busy")).toHaveLength(1);
    expect(screen.queryByText(/Conversation is busy/)).toBeNull();
    // Not part of the conversation, and what the user typed meanwhile stays.
    expect(screen.getAllByText("Zweite")).toHaveLength(1);
    expect(composerText()).toBe("Tippe weiter");
    expect(getDraft("c1")?.queued).toEqual({ text: "Zweite", reason: "assistant_error_conversation_busy" });
  });

  it("sends the queued message once under StrictMode", async () => {
    const run = runningAnswer();
    sendMessages
      .mockResolvedValueOnce(run.body)
      .mockResolvedValueOnce(stream([...START2, ...text("Zwei"), ...FINISH]));
    renderChat({}, { strict: true });
    send("Eins");
    await screen.findByText("Teil");
    send("Zweite Frage");
    await run.end(FINISH);
    await screen.findByText("Zwei");
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 20));
    });
    expect(sendMessages).toHaveBeenCalledTimes(2);
    expect(screen.getAllByText("Zweite Frage")).toHaveLength(1);
  });

  it("shows a queued message of a read-only conversation as not sent", () => {
    saveDraft("c1", { queued: { text: "Wartet noch", reason: null } });
    renderChat({ readOnly: { kind: "lost" } });
    expect(screen.getByText("assistant_draft_not_sent")).toBeTruthy();
    expect(screen.getByText("Wartet noch")).toBeTruthy();
    noQueue();
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(sendMessages).not.toHaveBeenCalled();
  });
});
