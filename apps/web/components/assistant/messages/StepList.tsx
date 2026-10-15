"use client";

import { Box, ButtonBase, Stack, Typography, useTheme } from "@mui/material";
import type { DynamicToolUIPart } from "ai";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { GOATLogoIconOnlyGreen } from "@p4b/ui/assets/svg/GOATLogoIconOnlyGreen";
import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { plainTranslate } from "@/lib/assistant/chips";
import { layerNames, stepLabel, stepResult, stepRows } from "@/lib/assistant/stepLabels";

import { focusRing, mutedText } from "@/components/assistant/styles";

const JSON_CHARS = 4000;
const RUNNING = new Set(["input-streaming", "input-available", "approval-requested", "approval-responded"]);
const MONO = "ui-monospace, SFMono-Regular, Menlo, monospace";

const pretty = (value: unknown): string => {
  const text = JSON.stringify(value, null, 2) ?? "";
  return text.length > JSON_CHARS ? `${text.slice(0, JSON_CHARS)}…` : text;
};

const rowSx = {
  // A button does not inherit the page font by itself.
  fontFamily: "inherit",
  width: "100%",
  justifyContent: "flex-start",
  alignItems: "flex-start",
  gap: "9px",
  px: "4px",
  py: "4px",
  borderRadius: "6px",
  textAlign: "left",
  "&:hover": { bgcolor: "action.hover" },
} as const;

/** Done, running (GOAT's mark) or failed, in one 14px slot. */
function StatusIcon({ state }: { state: "done" | "running" | "failed" }) {
  const theme = useTheme();
  if (state === "running") {
    return <GOATLogoIconOnlyGreen style={{ width: 14, height: 14, flexShrink: 0, marginTop: 2 }} />;
  }
  const failed = state === "failed";
  return (
    <Box
      sx={{
        width: 14,
        height: 14,
        mt: "2px",
        flexShrink: 0,
        borderRadius: "50%",
        border: 1,
        borderColor: failed ? "error.main" : mutedText,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}>
      <Icon
        iconName={failed ? ICON_NAME.CLOSE : ICON_NAME.CHECK}
        style={{ fontSize: 7, color: failed ? theme.palette.error.main : mutedText(theme) }}
      />
    </Box>
  );
}

/**
 * The tools an answer used (spec §4.7, §10): one line per call with what it
 * found, its input and result on click. The list never folds: the lines are
 * short, and they show how the answer came about.
 */
export default function StepList({ steps }: { steps: DynamicToolUIPart[] }) {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const [open, setOpen] = useState<string | null>(null);
  const rows = stepRows(steps);
  const names = layerNames(steps);
  // The labels carry the call's arguments (search words, layer names): React escapes them as text.
  const translate = plainTranslate(t);

  return (
    <Stack gap="1px">
      {rows.map(({ step, rejected }) => {
        const expanded = open === step.toolCallId;
        const output = (step as { output?: unknown }).output;
        const failed = step.state === "output-error";
        const result = failed ? t("assistant_step_failed") : stepResult(step, translate);
        const extras = [result, rejected.length ? t("assistant_step_retried") : null].filter(Boolean);
        return (
          <Box key={step.toolCallId}>
            <ButtonBase
              onClick={() => setOpen(expanded ? null : step.toolCallId)}
              aria-expanded={expanded}
              sx={{ ...rowSx, ...focusRing(theme) }}>
              <StatusIcon state={RUNNING.has(step.state) ? "running" : failed ? "failed" : "done"} />
              <Typography
                sx={{ flex: 1, minWidth: 0, fontSize: 12.5, lineHeight: 1.5, overflowWrap: "anywhere" }}>
                <Box component="span" sx={{ color: "text.primary" }}>
                  {stepLabel(step, names, translate)}
                </Box>
                {extras.map((extra) => (
                  <Box
                    key={extra}
                    component="span"
                    sx={{ color: failed && extra === result ? "error.main" : mutedText }}>
                    {` · ${extra}`}
                  </Box>
                ))}
              </Typography>
            </ButtonBase>
            {expanded && (
              <Box
                component="pre"
                sx={{
                  m: "2px 0 6px 27px",
                  px: "11px",
                  py: "10px",
                  border: 1,
                  borderColor: "divider",
                  borderRadius: "10px",
                  bgcolor: "background.default",
                  color: mutedText,
                  fontFamily: MONO,
                  fontSize: 11,
                  lineHeight: 1.7,
                  whiteSpace: "pre-wrap",
                  overflowWrap: "anywhere",
                  maxHeight: 280,
                  overflowY: "auto",
                }}>
                {[
                  // The tool's own name, for whoever wants to know what ran.
                  step.toolName,
                  // Rejected attempts first, in the order the model made them. The server's error text
                  // is English and may quote the service, so only the translated mark is shown.
                  ...rejected.map(
                    (attempt) =>
                      `${t("assistant_step_rejected")}\n${pretty(attempt.input)}\n${t("assistant_step_failed")}`
                  ),
                  `${t("assistant_step_input")}\n${pretty(step.input)}`,
                  ...(output === undefined ? [] : [`${t("assistant_step_output")}\n${pretty(output)}`]),
                ].join("\n\n")}
              </Box>
            )}
          </Box>
        );
      })}
    </Stack>
  );
}
