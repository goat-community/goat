"use client";

import { Box, ButtonBase, Stack, Typography, alpha, useTheme } from "@mui/material";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { plainTranslate } from "@/lib/assistant/chips";
import { useConversations } from "@/lib/assistant/conversations";
import { conversationTitle, originLabel } from "@/lib/assistant/history";
import { openConversation, useActiveSurface } from "@/lib/assistant/store";

import { CARD_RADIUS, accentSoft, focusRing, mutedText } from "@/components/assistant/styles";

const RECENT_COUNT = 5;

/** The full-screen start page's way back into earlier work: the newest conversations. */
function RecentConversations() {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const translate = plainTranslate(t);
  const { conversations } = useConversations({});
  const recent = conversations.slice(0, RECENT_COUNT);
  if (!recent.length) return null;
  return (
    <Box
      sx={{
        width: "100%",
        border: 1,
        borderColor: "divider",
        borderRadius: "14px",
        p: "16px",
        pb: "10px",
        bgcolor: "background.paper",
      }}>
      <Typography sx={{ fontSize: 14, fontWeight: 700, color: "text.primary" }}>
        {t("assistant_recent_title")}
      </Typography>
      <Typography sx={{ fontSize: 12.5, mt: "2px", mb: "8px", color: mutedText }}>
        {t("assistant_recent_sub")}
      </Typography>
      <Stack gap="2px">
        {recent.map((conversation) => (
          <ButtonBase
            key={conversation.id}
            onClick={() => openConversation(conversation.id)}
            sx={{
              // A button does not inherit the page font by itself.
              fontFamily: "inherit",
              justifyContent: "flex-start",
              gap: "10px",
              px: "12px",
              mx: "-8px",
              py: "8px",
              borderRadius: "8px",
              textAlign: "left",
              "&:hover": { bgcolor: "action.hover" },
              ...focusRing(theme),
            }}>
            <Typography
              noWrap
              sx={{ flex: 1, minWidth: 0, fontSize: 13, fontWeight: 600, color: "text.primary" }}>
              {conversationTitle(conversation, translate)}
            </Typography>
            <Typography noWrap sx={{ maxWidth: "40%", fontSize: 11.5, color: mutedText }}>
              {originLabel(conversation, translate)}
            </Typography>
            <Icon
              iconName={ICON_NAME.CHEVRON_RIGHT}
              style={{ fontSize: 11, flexShrink: 0, color: theme.palette.text.secondary }}
            />
          </ButtonBase>
        ))}
      </Stack>
    </Box>
  );
}

/** The start of a new conversation: what the assistant can do here, and three starters. */
export default function EmptyState({ onPick, big }: { onPick: (text: string) => void; big?: boolean }) {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const surface = useActiveSurface();
  const group = surface?.surface === "catalog" ? "catalog" : surface ? "project" : "none";
  return (
    <Stack gap={big ? "22px" : "12px"} alignItems={big ? "center" : "stretch"} sx={{ pt: big ? "6vh" : 0 }}>
      <Stack gap={big ? "8px" : "6px"} alignItems={big ? "center" : "stretch"}>
        <Typography
          component="h2"
          sx={{
            m: 0,
            fontSize: big ? 30 : 16,
            fontWeight: 700,
            letterSpacing: big ? "-0.8px" : "-0.2px",
            lineHeight: 1.25,
            textAlign: big ? "center" : "left",
            color: "text.primary",
          }}>
          {t(`assistant_empty_heading_${group}`)}
        </Typography>
        <Typography
          sx={{
            fontSize: big ? 14 : 13,
            lineHeight: 1.55,
            textAlign: big ? "center" : "left",
            color: mutedText,
            maxWidth: 560,
          }}>
          {t(`assistant_empty_sub_${group}`)}
        </Typography>
      </Stack>
      <Stack
        direction={big ? "row" : "column"}
        flexWrap="wrap"
        gap="10px"
        justifyContent="center"
        sx={{ width: "100%" }}>
        {[1, 2, 3].map((n) => {
          const text = t(`assistant_suggestion_${group}_${n}`);
          return (
            <ButtonBase
              key={n}
              onClick={() => onPick(text)}
              sx={{
                fontFamily: "inherit",
                justifyContent: "flex-start",
                textAlign: "left",
                flex: big ? "0 1 auto" : undefined,
                maxWidth: big ? 300 : "none",
                px: "13px",
                py: "10px",
                border: 1,
                borderColor: "divider",
                borderRadius: CARD_RADIUS,
                bgcolor: "background.paper",
                color: "text.primary",
                fontSize: 13,
                lineHeight: 1.45,
                transition: theme.transitions.create(["border-color", "background-color"], { duration: 120 }),
                "&:hover": {
                  borderColor: alpha(theme.palette.primary.main, 0.6),
                  bgcolor: accentSoft(theme),
                },
                ...focusRing(theme),
              }}>
              {text}
            </ButtonBase>
          );
        })}
      </Stack>
      {big && <RecentConversations />}
    </Stack>
  );
}
