import { DefaultChatTransport, type TextUIPart } from "ai";
import { getSession } from "next-auth/react";

import { assistantFetch, authHeaders } from "@/lib/assistant/http";
import type {
  AnswerFeedback,
  AssistantMessage,
  ConversationDetail,
  ConversationRecord,
  Locale,
  PageContext,
  Rating,
} from "@/lib/assistant/types";
import { ASSISTANT_BASE_URL } from "@/lib/constants";

export interface TransportOptions {
  /** The run that was active when the conversation was loaded; read at reconnect time. */
  getActiveRunId?: () => string | null | undefined;
  getLocale?: () => Locale;
}

/** The newest user message: the only one the server needs (it keeps the history). */
export function lastUserMessage(messages: AssistantMessage[]): { id: string; text: string } {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role !== "user") continue;
    const text = message.parts
      .filter((part): part is TextUIPart => part.type === "text")
      .map((part) => part.text)
      .join("");
    return { id: message.id, text };
  }
  throw new Error("There is no message to send.");
}

/**
 * The user's refresh token, so a detached run outlives the access token (spec
 * §6.5 fallback, plan 3). None without a session (AUTH=False).
 */
async function refreshToken(): Promise<string | null> {
  try {
    const session = await getSession();
    const token = (session as { refresh_token?: unknown } | null)?.refresh_token;
    return typeof token === "string" && token ? token : null;
  } catch {
    return null;
  }
}

/**
 * The AI SDK transport for one conversation (spec §6.1/§6.2).
 *
 * Only the new message goes to the server, with the context of the page it was
 * sent from (passed as `sendMessage(..., { body: { context } })`). Regenerating
 * an answer is not offered (spec §1 non-goals). `useChat({ resume: true })`
 * reconnects through `/stream`, which replays from the start of the run; the
 * dock only does that with a fresh chat (Task 9).
 */
export function createAssistantTransport(
  conversationId: string,
  options: TransportOptions = {}
): DefaultChatTransport<AssistantMessage> {
  const base = `${ASSISTANT_BASE_URL}/conversations/${conversationId}`;
  return new DefaultChatTransport<AssistantMessage>({
    api: `${base}/runs`,
    prepareSendMessagesRequest: async ({ messages, body, trigger }) => {
      if (trigger !== "submit-message") throw new Error("The assistant does not regenerate answers.");
      const context = (body as { context?: PageContext | null } | undefined)?.context ?? null;
      const refresh = await refreshToken();
      return {
        body: {
          message: lastUserMessage(messages),
          context,
          locale: options.getLocale?.() ?? "en",
          ...(refresh ? { refresh_token: refresh } : {}),
        },
        headers: await authHeaders(),
      };
    },
    prepareReconnectToStreamRequest: async () => {
      const runId = options.getActiveRunId?.();
      return {
        api: runId ? `${base}/stream?run_id=${encodeURIComponent(runId)}` : `${base}/stream`,
        headers: await authHeaders(),
      };
    },
  });
}

export const createConversation = (originSurface: string, projectId?: string | null) =>
  assistantFetch<ConversationRecord>("/conversations", {
    method: "POST",
    body: { origin_surface: originSurface, project_id: projectId ?? null },
  });

export async function fetchConversation(conversationId: string): Promise<ConversationDetail> {
  const body = await assistantFetch<{
    conversation: ConversationRecord;
    messages: AssistantMessage[];
    active_run_id: string | null;
    access?: "ok" | "lost";
    project_name?: string | null;
    feedback?: Record<string, AnswerFeedback>;
  }>(`/conversations/${conversationId}`);
  return {
    conversation: body.conversation,
    messages: body.messages,
    activeRunId: body.active_run_id ?? null,
    access: body.access ?? "ok",
    projectName: body.project_name ?? null,
    feedback: body.feedback ?? {},
  };
}

/** Rates an answer, or with `rating` null removes the rating. */
export const saveFeedback = (
  conversationId: string,
  messageId: string,
  rating: Rating | null,
  comment: string | null = null
) =>
  assistantFetch<{ rating: Rating | null; comment: string | null }>(
    `/conversations/${conversationId}/messages/${messageId}/feedback`,
    { method: "PUT", body: { rating, comment } }
  );

/** Server-side stop. `useChat().stop()` only drops the connection when resume is on. */
export const cancelAssistantRun = (conversationId: string) =>
  assistantFetch<void>(`/conversations/${conversationId}/cancel`, { method: "POST" });
