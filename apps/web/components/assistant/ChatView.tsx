"use client";

import { useChat } from "@ai-sdk/react";
import { Alert, Box, Button, CircularProgress, Stack, Typography, useTheme } from "@mui/material";
import type { ChatStatus } from "ai";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { announceRunEnd, lastAnswer, runEndOf } from "@/lib/assistant/announce";
import { type Translate, plain, plainTranslate } from "@/lib/assistant/chips";
import { refreshConversationLists } from "@/lib/assistant/conversations";
import { assistantErrorKey, toRequestError } from "@/lib/assistant/errors";
import {
  type QueuedMessage,
  addPendingRun,
  clearFirstMessage,
  getDraft,
  removePendingRun,
  saveDraft,
  setDockState,
  useActiveSurface,
  useDockState,
} from "@/lib/assistant/store";
import { cancelAssistantRun, createAssistantTransport } from "@/lib/assistant/transport";
import type { AnswerFeedback, AssistantMessage, Locale, PageContext } from "@/lib/assistant/types";

import Composer from "@/components/assistant/Composer";
import { useDockActions } from "@/components/assistant/DockActions";
import QueuedItem from "@/components/assistant/QueuedItem";
import DockNote from "@/components/assistant/messages/DockNote";
import MessageList from "@/components/assistant/messages/MessageList";
import { composerFooterSx, mutedText, neutralPillSx, pillButtonSx } from "@/components/assistant/styles";
import { useComposerContext } from "@/components/assistant/useComposerContext";

/** How long Stop waits for the server's own end of the run before it drops the connection. */
export const STOP_GRACE_MS = 5000;
const STOP_POLL_MS = 50;

export type ReadOnlyReason =
  | { kind: "elsewhere"; projectId: string; projectName: string | null }
  | { kind: "lost" };

export interface ChatViewProps {
  conversationId: string;
  title: string;
  /** The project the conversation is bound to; null while unbound. */
  projectId: string | null;
  projectName: string | null;
  initialMessages: AssistantMessage[];
  /** The user's ratings of the loaded answers, by answer id. */
  initialFeedback?: Record<string, AnswerFeedback>;
  activeRunId: string | null;
  /** Re-attach to the active run on mount (a fresh chat only, Global Constraints). */
  resume: boolean;
  readOnly: ReadOnlyReason | null;
  /** The page's project is not known yet: neither the composer nor a read-only notice. */
  waiting?: boolean;
  /** The message that created this conversation, sent once on mount. */
  firstMessage: { text: string; context: PageContext | null } | null;
  /** The first message went out (the parent stops passing it). */
  onFirstMessageSent?: () => void;
  /** Remount with fresh state after a dropped connection. */
  onReconnect: () => void;
  /** The server bound the conversation to a project (a send from a project page, or a 409 naming it). */
  onBound?: (projectId: string, projectName: string | null) => void;
  /**
   * The server refused a request because the user lost access to a project of
   * the conversation. `messages` is what the chat holds then, without a refused send.
   */
  onAccessLost?: (messages: AssistantMessage[]) => void;
  big?: boolean;
}

/** Everything from the newest user message on: what the server refused to store. */
export function dropLastUserMessage(list: AssistantMessage[]): AssistantMessage[] {
  for (let index = list.length - 1; index >= 0; index -= 1) {
    if (list[index].role === "user") return list.slice(0, index);
  }
  return list;
}

const hasRunStatus = (message: AssistantMessage | undefined) =>
  !!message && message.role === "assistant" && message.parts.some((part) => part.type === "data-run-status");

const isBusy = (status: ChatStatus) => status === "submitted" || status === "streaming";

/** The run of this conversation ended: forget it as pending, refresh the history (titles), announce it. */
function endRun(conversationId: string, message: AssistantMessage, title: string, t: Translate): void {
  removePendingRun(conversationId);
  void refreshConversationLists();
  void announceRunEnd({ conversationId, messageId: message.id, title, status: runEndOf(message) }, t);
}

function ReadOnlyNotice({ reason }: { reason: ReadOnlyReason }) {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const actions = useDockActions();
  const newHere = (
    <Button
      variant="outlined"
      color="inherit"
      size="small"
      onClick={actions.newConversationHere}
      sx={neutralPillSx(theme)}>
      {t("assistant_new_here")}
    </Button>
  );
  if (reason.kind === "lost") {
    return (
      <Stack gap="10px" alignItems="flex-start">
        <DockNote tone="info">{t("assistant_lost_access")}</DockNote>
        {newHere}
      </Stack>
    );
  }
  return (
    <Stack gap="10px">
      <Typography sx={{ fontSize: 13, lineHeight: 1.5, color: mutedText }}>
        {reason.projectName
          ? t("assistant_readonly_elsewhere", plain({ name: reason.projectName }))
          : t("assistant_readonly_elsewhere_unnamed")}
      </Typography>
      <Stack direction="row" gap="8px" flexWrap="wrap">
        <Button
          variant="contained"
          size="small"
          onClick={() => void actions.openInProject(reason.projectId)}
          sx={{ ...pillButtonSx, "&&": { ...pillButtonSx["&&"], px: "18px" } }}>
          {t("assistant_open_in_project")}
        </Button>
        {newHere}
      </Stack>
    </Stack>
  );
}

/**
 * One conversation with AI SDK v7 `useChat`. Mounted per conversation (and
 * per reconnect): the parent keys it, so a chat never carries state from
 * another conversation or from before a dropped connection.
 */
export default function ChatView(props: ChatViewProps) {
  const { conversationId } = props;
  const { t, i18n } = useTranslation("common");
  const dock = useDockState();
  const surface = useActiveSurface();
  const composer = useComposerContext(conversationId);
  const activeRun = useRef(props.activeRunId);
  const locale = useRef<Locale>("en");
  const lastSent = useRef("");
  const sentFirst = useRef(false);
  /**
   * Set while a request of ours is out: only its refusal may undo a message (a
   * resume never does). "queued" when it carries the queued message.
   */
  const inFlight = useRef<"send" | "queued" | null>(null);
  /** The project an unbound conversation becomes bound to when the server accepts the send. */
  const pendingBind = useRef<{ projectId: string; name: string | null } | null>(null);
  /** A TypeError the AI SDK did not recognise as a dropped connection (Safari: "Load failed"). */
  const brokeOff = useRef(false);
  const statusRef = useRef<ChatStatus>("ready");
  const scrollRef = useRef<HTMLDivElement>(null);
  // Restored after a remount (expanding or collapsing the dock); see `saveDraft`.
  const [draft, setDraft] = useState(() => getDraft(conversationId)?.text ?? "");
  const changeDraft = (value: string) => {
    setDraft(value);
    saveDraft(conversationId, { text: value });
  };
  // Sent while an answer ran: kept next to the draft, so a remount still shows it.
  const [queued, setQueuedState] = useState<QueuedMessage | null>(
    () => getDraft(conversationId)?.queued ?? null
  );
  const setQueued = (value: QueuedMessage | null) => {
    setQueuedState(value);
    saveDraft(conversationId, { queued: value });
  };
  /** Adds `text` to the queued message (before or after its text), or queues it. */
  const queue = (
    text: string,
    { reason = null, first = false }: { reason?: string | null; first?: boolean } = {}
  ) => {
    // The store, not the state: a callback of an older render may call this.
    const current = getDraft(conversationId)?.queued?.text;
    setQueued({ text: current ? (first ? `${text}\n${current}` : `${current}\n${text}`) : text, reason });
  };
  /**
   * Send the queued message once nothing runs: set when an answer ended
   * normally, or by "Send now". A failed or stopped answer does not set it.
   */
  const [releaseQueued, setReleaseQueued] = useState(false);
  /** The queued message's send was refused: its item shows the reason, the transcript does not. */
  const [queueRefused, setQueueRefused] = useState(false);
  /** A Stop is under way; a send now could be cancelled by its late second cancel. */
  const [stopping, setStopping] = useState(false);
  const [disconnected, setDisconnected] = useState(false);
  const [stopError, setStopError] = useState<string | null>(null);
  /**
   * Stop was pressed before the server started the run: that cancel may have
   * found no run to stop, so it is sent again once the stream starts.
   */
  const cancelAgain = useRef(false);
  /** The composer's chips and sources clear only when the server accepted the send. */
  const resetOnAccept = useRef(false);
  // Resume is decided at mount: useChat would resume a live chat if it turned true later.
  const [resume] = useState(props.resume);

  useEffect(() => {
    locale.current = i18n.language?.startsWith("de") ? "de" : "en";
  }, [i18n.language]);

  // One transport per conversation; the run id and the language are read when used.
  const transport = useMemo(
    () =>
      createAssistantTransport(conversationId, {
        getActiveRunId: () => activeRun.current,
        getLocale: () => locale.current,
      }),
    [conversationId]
  );

  const reportBinding = () => {
    const binding = pendingBind.current;
    pendingBind.current = null;
    if (binding) props.onBound?.(binding.projectId, binding.name);
  };

  /** The server accepted the send: it bound the conversation, and the composer starts afresh. */
  const accepted = () => {
    reportBinding();
    if (resetOnAccept.current) {
      resetOnAccept.current = false;
      composer.reset();
      // The history marks the conversation as running.
      void refreshConversationLists();
    }
  };

  const { messages, sendMessage, stop, status, error, setMessages } = useChat<AssistantMessage>({
    id: conversationId,
    messages: props.initialMessages,
    resume,
    transport,
    onError: (err) => {
      const refused = toRequestError(err);
      /** The chat's messages now, read from the chat itself (this callback's render may be older). */
      let live: AssistantMessage[] | null = null;
      if (refused && inFlight.current) {
        // Refused before anything was stored: the message is not part of the
        // conversation. Its text, chips and sources go back into the composer;
        // a queued message goes back into the queue, ahead of what was queued since.
        setMessages((list) => (live = dropLastUserMessage(list)));
        if (inFlight.current === "queued") {
          queue(lastSent.current, { reason: assistantErrorKey(refused), first: true });
          setQueueRefused(true);
        } else changeDraft(lastSent.current);
        removePendingRun(conversationId);
        pendingBind.current = null;
        resetOnAccept.current = false;
        if (refused.code === "conversation_bound" && refused.projectId)
          props.onBound?.(refused.projectId, null);
      } else if (!refused && err instanceof TypeError) {
        brokeOff.current = true;
      }
      if (refused?.code === "project_access_lost") {
        if (live === null) setMessages((list) => (live = list));
        props.onAccessLost?.(live ?? []);
      }
    },
    onFinish: ({ message, isDisconnect, isAbort, isError }) => {
      inFlight.current = null;
      activeRun.current = null;
      cancelAgain.current = false;
      // The server answered with parts: it accepted the run, so it bound the conversation.
      if (message.role === "assistant" && message.parts.length > 0) accepted();
      pendingBind.current = null;
      resetOnAccept.current = false;
      if (isDisconnect || brokeOff.current) {
        brokeOff.current = false;
        // The run goes on server side; a reconnect (fresh chat) shows the rest.
        setDisconnected(true);
        return;
      }
      // A connection this view dropped itself (closed dock, other conversation)
      // or a refused request did not end the run.
      const ended = (!isAbort && !isError) || hasRunStatus(message);
      if (ended && message.role === "assistant") {
        // React escapes the title itself; the toast takes a plain string.
        endRun(
          conversationId,
          message,
          props.title || lastSent.current || t("assistant_untitled"),
          plainTranslate(t)
        );
        // Only an answer that ended normally sends the queued message by itself.
        if (runEndOf(message) === "succeeded" && getDraft(conversationId)?.queued) setReleaseQueued(true);
      }
    },
  });

  const busy = isBusy(status);
  useEffect(() => {
    statusRef.current = status;
    if (status !== "streaming") return;
    // Streaming means the server accepted the send (or the replay began).
    accepted();
    if (cancelAgain.current) {
      cancelAgain.current = false;
      void cancelAssistantRun(conversationId).catch(() => undefined);
    }
  });

  const send = async (text: string, context: PageContext | null, fromQueue = false) => {
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    lastSent.current = trimmed;
    inFlight.current = fromQueue ? "queued" : "send";
    const pageProject = context && "project_id" in context ? context.project_id : null;
    pendingBind.current =
      !props.projectId && pageProject
        ? { projectId: pageProject, name: surface?.project?.name ?? null }
        : null;
    // Cleared at once so a remount while the request is out shows no stale text;
    // a refusal puts it back (onError). A queued message leaves what the user types meanwhile.
    if (fromQueue) setQueued(null);
    else changeDraft("");
    setQueueRefused(false);
    setStopError(null);
    setDisconnected(false);
    cancelAgain.current = false;
    resetOnAccept.current = true;
    addPendingRun({
      conversationId,
      title: props.title || trimmed.slice(0, 80),
      since: Date.now(),
      // RunWatcher announces only a newer answer than this one.
      knownAnswerId: lastAnswer(messages)?.id ?? null,
    });
    const parts: AssistantMessage["parts"] = [{ type: "text", text: trimmed }];
    if (context) parts.push({ type: "data-context", data: context });
    await sendMessage({ parts }, { body: { context } });
  };
  // Read through a ref: `send` is new on every render, and the first-message
  // timer below must be armed once, not again on each render.
  const sendRef = useRef(send);
  const firstSentRef = useRef(props.onFirstMessageSent);
  const contextRef = useRef(composer.context);
  useEffect(() => {
    sendRef.current = send;
    firstSentRef.current = props.onFirstMessageSent;
    contextRef.current = composer.context;
  });

  useEffect(() => {
    const first = props.firstMessage;
    if (!first || sentFirst.current) return;
    // React StrictMode mounts, unmounts and mounts again, and useChat's cleanup
    // stops the chat in between: the send waits for the mount that stays.
    const timer = window.setTimeout(() => {
      if (sentFirst.current) return;
      sentFirst.current = true;
      clearFirstMessage(conversationId);
      firstSentRef.current?.();
      void sendRef.current(first.text, first.context);
    }, 0);
    return () => window.clearTimeout(timer);
  }, [conversationId, props.firstMessage]);

  const readOnly = !!props.readOnly;
  // The queued message goes once nothing runs and no Stop is still settling (its late
  // cancel could stop the new run). The flag is cleared first: a further pass sends nothing.
  useEffect(() => {
    if (!releaseQueued || busy || stopping || props.waiting || readOnly) return;
    setReleaseQueued(false);
    const next = getDraft(conversationId)?.queued;
    if (next) void sendRef.current(next.text, contextRef.current, true);
  }, [releaseQueued, busy, stopping, props.waiting, readOnly, conversationId]);

  // The queued item takes room from the transcript: its newest message stays in view.
  useEffect(() => {
    const element = scrollRef.current;
    if (element) element.scrollTop = element.scrollHeight;
  }, [messages, status, queued]);

  useEffect(() => {
    if (dock.review?.conversationId !== conversationId) return;
    const target = scrollRef.current?.querySelector(`[data-part-id=${JSON.stringify(dock.review.partId)}]`);
    if (!target) return;
    (target as HTMLElement).scrollIntoView?.({ block: "center" });
    setDockState({ review: null });
  }, [dock.review, conversationId, messages]);

  /**
   * Set when this chat unmounts. A Stop still waiting then gives up without a
   * late cancel: the reopened conversation may run a new answer by then.
   */
  const unmounted = useRef(false);
  /** The pending poll of `settled`, so an unmount can clear it at once. */
  const stopWait = useRef<{ timer: ReturnType<typeof setTimeout>; resolve: () => void } | null>(null);
  useEffect(() => {
    // StrictMode unmounts and mounts again: the mount that stays is live.
    unmounted.current = false;
    return () => {
      unmounted.current = true;
      const wait = stopWait.current;
      stopWait.current = null;
      if (wait) {
        clearTimeout(wait.timer);
        wait.resolve();
      }
    };
  }, []);

  /** True when the stream ended by itself within STOP_GRACE_MS (or the chat unmounted). */
  const settled = async (): Promise<boolean> => {
    const deadline = Date.now() + STOP_GRACE_MS;
    while (Date.now() < deadline) {
      if (unmounted.current || !isBusy(statusRef.current)) return true;
      await new Promise<void>((resolve) => {
        const timer = setTimeout(() => {
          stopWait.current = null;
          resolve();
        }, STOP_POLL_MS);
        stopWait.current = { timer, resolve };
      });
    }
    return unmounted.current || !isBusy(statusRef.current);
  };

  const stopRun = async () => {
    setStopError(null);
    // Before the stream starts the server may not have begun the run yet; its
    // cancel then finds nothing, and the run would go on (spec §6.1.5).
    cancelAgain.current = statusRef.current === "submitted";
    try {
      // Stop the run on the server: stop() alone only drops this connection.
      await cancelAssistantRun(conversationId);
    } catch (err) {
      if (unmounted.current) return;
      // The server could not be told; free the composer now. The run may go on,
      // so "Send now" does not send: the queued message stays.
      setReleaseQueued(false);
      cancelAgain.current = false;
      setStopError(assistantErrorKey(err));
      await stop();
      removePendingRun(conversationId);
      return;
    }
    // The cancelled run's stream ends with its run-status part ("Stopped."), live
    // as after a reload; only a stream that does not end is dropped.
    const ended = await settled();
    // Unmounted meanwhile: useChat's cleanup dropped the connection, and a late
    // cancel could stop a run started since in the reopened conversation.
    if (unmounted.current) return;
    if (!ended) {
      // Tell the server once more (the run may have started since), then drop the connection.
      cancelAgain.current = false;
      await cancelAssistantRun(conversationId).catch(() => undefined);
      await stop();
    }
    removePendingRun(conversationId);
  };

  const onStop = async () => {
    setStopping(true);
    try {
      await stopRun();
    } finally {
      if (!unmounted.current) setStopping(false);
    }
  };

  /** Send, or queue while an answer runs; with a message queued already, the text joins it. */
  const submit = () => {
    const text = draft.trim();
    if (!text) return;
    if (!busy && !stopping && !queued) {
      void send(draft, composer.context);
      return;
    }
    queue(text);
    changeDraft("");
    // Nothing runs: the joined message goes at once.
    if (!busy && !stopping) setReleaseQueued(true);
  };

  /** "Send now": stop the running answer the way Stop does, then send the queued message. */
  const sendNow = () => {
    setReleaseQueued(true);
    if (busy && !stopping) void onStop();
  };

  /** "Remove": nothing is queued any more, and its text goes back into the composer. */
  const removeQueued = () => {
    if (!queued) return;
    setQueued(null);
    setReleaseQueued(false);
    changeDraft(draft.trim() ? `${queued.text}\n${draft}` : queued.text);
  };

  const last = messages[messages.length - 1];
  // A dropped connection has its own banner; a failed run its own note.
  // A refusal the read-only notice explains needs no second note.
  const refusedCode = toRequestError(error)?.code;
  const explained =
    !!props.readOnly && (refusedCode === "project_access_lost" || refusedCode === "conversation_bound");
  // A refused queued message shows the reason in its own item.
  const errorKey =
    error && !disconnected && !explained && !queueRefused && !hasRunStatus(last)
      ? assistantErrorKey(error)
      : null;
  // A read-only conversation sends nothing: what the user wrote stays readable (and copyable).
  const unsent = [queued?.text ?? "", draft].filter((text) => text.trim());

  return (
    <Stack sx={{ flex: 1, minHeight: 0 }}>
      <Box
        ref={scrollRef}
        sx={{ flex: 1, overflowY: "auto", px: props.big ? "24px" : "16px", py: props.big ? "24px" : "18px" }}>
        <Stack gap="14px" sx={{ maxWidth: props.big ? 720 : "none", mx: "auto" }}>
          <MessageList
            messages={messages}
            busy={busy}
            conversationId={conversationId}
            conversationProjectId={props.projectId}
            projectName={props.projectName}
            readOnly={!!props.readOnly}
            feedback={props.initialFeedback}
          />
          {disconnected && (
            <Alert
              severity="warning"
              action={
                <Button color="inherit" size="small" onClick={props.onReconnect}>
                  {t("assistant_reconnect")}
                </Button>
              }>
              {t("assistant_disconnected")}
            </Alert>
          )}
          {errorKey && <Alert severity="error">{t(errorKey)}</Alert>}
          {stopError && <Alert severity="error">{t(stopError)}</Alert>}
        </Stack>
      </Box>
      <Box sx={composerFooterSx(props.big)}>
        <Box sx={{ maxWidth: props.big ? 720 : "none", mx: "auto" }}>
          {props.waiting ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: "8px" }}>
              <CircularProgress size={20} />
            </Box>
          ) : props.readOnly ? (
            <Stack gap="12px">
              {unsent.length > 0 && (
                // A refused or queued message stays readable (and copyable) when the composer gives way to the notice.
                <Box>
                  <Typography sx={{ fontSize: 12, color: mutedText }}>
                    {t("assistant_draft_not_sent")}
                  </Typography>
                  {unsent.map((text, index) => (
                    <Typography
                      key={index}
                      sx={{
                        mt: "4px",
                        px: "12px",
                        py: "8px",
                        borderRadius: "10px",
                        fontSize: 13,
                        color: "text.primary",
                        bgcolor: "action.hover",
                        whiteSpace: "pre-wrap",
                        overflowWrap: "anywhere",
                      }}>
                      {text}
                    </Typography>
                  ))}
                </Box>
              )}
              <ReadOnlyNotice reason={props.readOnly} />
            </Stack>
          ) : (
            <>
              {queued && <QueuedItem queued={queued} onSendNow={sendNow} onRemove={removeQueued} />}
              <Composer
                draft={draft}
                onDraftChange={changeDraft}
                busy={busy}
                queueWhileBusy
                onSend={submit}
                onStop={() => void onStop()}
                chips={composer.chips}
                onRemoveChip={composer.removeChip}
                mentionsEnabled={composer.mentionsEnabled}
                onAddSource={composer.addSource}
                sourcesFull={composer.sourcesFull}
                excludeProjectId={composer.projectId}
                big={props.big}
              />
            </>
          )}
        </Box>
      </Box>
    </Stack>
  );
}
