"use client";

import { Box, Stack, Typography } from "@mui/material";
import { alpha, keyframes } from "@mui/material/styles";
import type { DynamicToolUIPart, TextUIPart } from "ai";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { GOATLogoIconOnlyGreen } from "@p4b/ui/assets/svg/GOATLogoIconOnlyGreen";

import { contextChips, plainTranslate } from "@/lib/assistant/chips";
import { SHOW_TOOLS, shownGroups } from "@/lib/assistant/items";
import type { AnswerFeedback, AssistantMessage, PageContext } from "@/lib/assistant/types";

import AnswerDetails from "@/components/assistant/messages/AnswerDetails";
import CaveatNote from "@/components/assistant/messages/CaveatNote";
import ContextChips from "@/components/assistant/messages/ContextChips";
import CopyAnswer from "@/components/assistant/messages/CopyAnswer";
import FeedbackButtons from "@/components/assistant/messages/FeedbackButtons";
import ProposalCard from "@/components/assistant/messages/ProposalCard";
import ResultCards from "@/components/assistant/messages/ResultCards";
import RunStatusNote from "@/components/assistant/messages/RunStatusNote";
import SafeMarkdown from "@/components/assistant/messages/SafeMarkdown";
import StepList from "@/components/assistant/messages/StepList";
import { accentSoft, accentText, mutedText } from "@/components/assistant/styles";

export interface MessageListProps {
  messages: AssistantMessage[];
  busy: boolean;
  conversationId: string;
  conversationProjectId: string | null;
  projectName: string | null;
  readOnly: boolean;
  /** The user's ratings, by answer id (from the loaded conversation). */
  feedback?: Record<string, AnswerFeedback>;
}

const lastProposalId = (messages: AssistantMessage[]): string | null => {
  for (let m = messages.length - 1; m >= 0; m -= 1) {
    const parts = messages[m].parts;
    for (let p = parts.length - 1; p >= 0; p -= 1) {
      const part = parts[p];
      if (part.type === "data-proposal") return part.id ?? `${messages[m].id}:${p}`;
    }
  }
  return null;
};

function UserMessage({ message, projectName }: { message: AssistantMessage; projectName: string | null }) {
  const { t } = useTranslation("common");
  const text = message.parts
    .filter((part): part is TextUIPart => part.type === "text")
    .map((part) => part.text)
    .join("");
  const context = message.parts.find((part) => part.type === "data-context")?.data as PageContext | undefined;
  const chips = contextChips(context ?? null, projectName ?? undefined, plainTranslate(t));
  return (
    <Stack gap="6px" alignItems="flex-end">
      <Box
        sx={(theme) => ({
          maxWidth: "85%",
          px: "14px",
          py: "9px",
          borderRadius: "14px 14px 4px 14px",
          bgcolor: accentSoft(theme),
          whiteSpace: "pre-wrap",
          overflowWrap: "anywhere",
        })}>
        {/* The colour goes on the text itself: the theme's body variants carry their own. */}
        <Typography
          sx={(theme) => ({ fontSize: 13.5, fontWeight: 600, lineHeight: 1.45, color: accentText(theme) })}>
          {text}
        </Typography>
      </Box>
      <ContextChips chips={chips} />
    </Stack>
  );
}

/** A band of light moving across the text, left to right. */
const shimmer = keyframes`
  from { background-position: 100% 0; }
  to { background-position: 0 0; }
`;

/** The answer is still coming, while nothing else on screen shows it. */
function AnsweringLine() {
  const { t } = useTranslation("common");
  return (
    <Stack direction="row" gap="8px" alignItems="center" role="status">
      <GOATLogoIconOnlyGreen style={{ width: 14, height: 14 }} />
      <Typography
        sx={(theme) => {
          const dim = alpha(theme.palette.text.primary, 0.45);
          const bright = theme.palette.text.primary;
          return {
            fontSize: 12.5,
            color: mutedText(theme),
            // Dim text with a bright band in the middle, three times as wide as the text,
            // so the band enters, crosses and leaves within one cycle.
            backgroundImage: `linear-gradient(90deg, ${dim} 0%, ${dim} 38%, ${bright} 50%, ${dim} 62%, ${dim} 100%)`,
            backgroundSize: "300% 100%",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            animation: `${shimmer} 1.8s ease-in-out infinite`,
            "@media (prefers-reduced-motion: reduce)": {
              animation: "none",
              backgroundImage: "none",
              WebkitTextFillColor: "currentColor",
            },
          };
        }}>
        {t("assistant_running")}
      </Typography>
    </Stack>
  );
}

function Answer({
  message,
  running,
  latest,
  newestProposal,
  conversationId,
  conversationProjectId,
  readOnly,
  feedback,
}: {
  message: AssistantMessage;
  running: boolean;
  /** The newest answer of the conversation. */
  latest: boolean;
  newestProposal: string | null;
  conversationId: string;
  conversationProjectId: string | null;
  readOnly: boolean;
  feedback?: AnswerFeedback;
}) {
  const blocks: ReactNode[] = [];
  let tools: DynamicToolUIPart[] = [];
  // Only the answer's last list of each card tool becomes cards: a model that
  // names them more than once has refined what it points to.
  const lastShown = SHOW_TOOLS.map((name) =>
    message.parts.findLast(
      (part): part is DynamicToolUIPart =>
        part.type === "dynamic-tool" && part.toolName === name && shownGroups(part).length > 0
    )
  ).filter((part): part is DynamicToolUIPart => part !== undefined);
  const flush = (key: string) => {
    if (!tools.length) return;
    const group = tools;
    tools = [];
    blocks.push(<StepList key={`steps-${key}`} steps={group} />);
    // In the answer's order, when it shows both kinds of cards.
    group
      .filter((part) => lastShown.includes(part))
      .forEach((part) =>
        blocks.push(<ResultCards key={`results-${key}-${part.toolCallId}`} groups={shownGroups(part)} />)
      );
  };
  message.parts.forEach((part, index) => {
    if (part.type === "dynamic-tool") {
      tools.push(part);
      return;
    }
    if (part.type === "step-start") return;
    flush(String(index));
    if (part.type === "text") {
      blocks.push(<SafeMarkdown key={index}>{part.text}</SafeMarkdown>);
    } else if (part.type === "data-proposal") {
      const partId = part.id ?? `${message.id}:${index}`;
      blocks.push(
        <ProposalCard
          key={partId}
          proposal={part.data}
          partId={partId}
          conversationId={conversationId}
          conversationProjectId={conversationProjectId}
          readOnly={readOnly}
          isLatest={partId === newestProposal}
        />
      );
    } else if (part.type === "data-caveat") {
      blocks.push(<CaveatNote key={index} data={part.data} />);
    } else if (part.type === "data-run-status") {
      blocks.push(<RunStatusNote key={index} data={part.data} />);
    }
  });
  flush("end");
  const text = message.parts
    .filter((part): part is TextUIPart => part.type === "text")
    .map((part) => part.text)
    .join("\n\n");
  // A stopped or failed answer keeps Copy for what it said, but has no details to show.
  const ended = message.parts.some((part) => part.type === "data-run-status");
  const actions = !running && (text.trim() || !ended);
  return (
    <Stack
      gap="14px"
      sx={{
        // The newest answer shows its actions; older ones on hover or keyboard focus, and
        // always without a hover (touch), so a long transcript is not full of icons.
        "& .answer-actions": { opacity: latest ? 1 : 0, transition: "opacity 120ms" },
        "&:hover .answer-actions, &:focus-within .answer-actions": { opacity: 1 },
        "@media (hover: none)": { "& .answer-actions": { opacity: 1 } },
      }}>
      {blocks}
      {/* For the whole run, below whatever came so far: between steps nothing else moves
          (the model decides what to do next), and staying put keeps the animation smooth. */}
      {running && <AnsweringLine />}
      {actions && (
        // The 28px buttons sit 6px out, so their icons start where the answer's text does.
        <Stack className="answer-actions" direction="row" gap="4px" sx={{ mt: "-8px", ml: "-6px" }}>
          <CopyAnswer text={text} />
          {!ended && <AnswerDetails usage={message.metadata?.usage} />}
          {!ended && (
            <FeedbackButtons conversationId={conversationId} messageId={message.id} initial={feedback} />
          )}
        </Stack>
      )}
    </Stack>
  );
}

/** The transcript: user messages with their context chips, answers part by part (spec §10). */
export default function MessageList(props: MessageListProps) {
  const newestProposal = lastProposalId(props.messages);
  const latestAnswer = props.messages.findLast((message) => message.role === "assistant")?.id;
  return (
    <Stack gap="20px">
      {props.messages.map((message, index) =>
        message.role === "user" ? (
          <UserMessage key={message.id} message={message} projectName={props.projectName} />
        ) : message.role === "assistant" ? (
          <Answer
            key={message.id}
            message={message}
            running={props.busy && index === props.messages.length - 1}
            latest={message.id === latestAnswer}
            newestProposal={newestProposal}
            conversationId={props.conversationId}
            conversationProjectId={props.conversationProjectId}
            readOnly={props.readOnly}
            feedback={props.feedback?.[message.id]}
          />
        ) : null
      )}
      {/* Sent, and the answer has not started yet. */}
      {props.busy && props.messages.at(-1)?.role === "user" && <AnsweringLine />}
    </Stack>
  );
}
