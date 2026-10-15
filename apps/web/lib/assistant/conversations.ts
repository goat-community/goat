import useSWR, { mutate } from "swr";

import { assistantFetch } from "@/lib/assistant/http";
import type { ConversationSummary } from "@/lib/assistant/types";
import { ASSISTANT_BASE_URL } from "@/lib/constants";

export const CONVERSATIONS_KEY = "assistant:conversations";

export const listConversations = ({ projectId, q }: { projectId?: string | null; q?: string }) =>
  assistantFetch<ConversationSummary[]>("/conversations", {
    query: { project_id: projectId ?? undefined, q: q?.trim() || undefined, limit: "100" },
  });

/** The history (spec §10): one project's conversations, or all of them. */
export function useConversations({
  projectId,
  q,
  enabled = true,
}: {
  projectId?: string | null;
  q?: string;
  enabled?: boolean;
}) {
  const key = enabled && ASSISTANT_BASE_URL ? [CONVERSATIONS_KEY, projectId ?? "", q?.trim() ?? ""] : null;
  const {
    data,
    error,
    isLoading,
    mutate: revalidate,
  } = useSWR<ConversationSummary[]>(
    key,
    (args: string[]) => listConversations({ projectId: args[1] || null, q: args[2] }),
    { revalidateOnFocus: false }
  );
  return { conversations: data ?? [], error, isLoading, mutate: revalidate };
}

export const updateConversation = (id: string, patch: { title?: string | null; project_id?: string }) =>
  assistantFetch<ConversationSummary>(`/conversations/${id}`, { method: "PATCH", body: patch });

export const deleteConversation = (id: string) =>
  assistantFetch<void>(`/conversations/${id}`, { method: "DELETE" });

/** Revalidate every history list (after a run ended, a rename, a delete). */
export const refreshConversationLists = () =>
  mutate((key) => Array.isArray(key) && key[0] === CONVERSATIONS_KEY);
