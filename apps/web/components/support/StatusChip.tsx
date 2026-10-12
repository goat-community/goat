"use client";

import { Box, alpha, darken, useTheme } from "@mui/material";
import type { Theme } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { SupportStatus, SupportTicket } from "@/lib/validations/support";

/** The palette colour each status is tinted with; `null` is the neutral grey. */
const TONE: Record<SupportStatus, "info" | "warning" | "success" | null> = {
  new: null,
  in_progress: "info",
  waiting: "warning",
  solved: "success",
  cancelled: null,
};

/** The status colour as text on its own 12% tint. In light mode the palette's
 * bright mains read too pale on a pale tint, so the text takes a darker shade. */
export const statusColor = (theme: Theme, status: SupportStatus): string => {
  const tone = TONE[status];
  if (!tone) return theme.palette.text.secondary;
  const main = theme.palette[tone].main;
  return theme.palette.mode === "light" ? darken(main, 0.22) : main;
};

type Props = { ticket: Pick<SupportTicket, "status" | "needs_my_reply" | "customer_name"> };

/** Status label as a small tinted pill with a dot; an admin looking at a colleague's waiting ticket sees who it waits for. */
const StatusChip = ({ ticket }: Props) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const label =
    ticket.status === "waiting" && !ticket.needs_my_reply && ticket.customer_name
      ? t("support_status_waiting_for", { name: ticket.customer_name })
      : t(`support_status_${ticket.status}`);
  const color = statusColor(theme, ticket.status);
  return (
    <Box
      component="span"
      sx={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        maxWidth: "100%",
        height: 22,
        px: "9px",
        borderRadius: "999px",
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: 0.2,
        lineHeight: 1,
        whiteSpace: "nowrap",
        color,
        backgroundColor: alpha(color, 0.12),
      }}>
      <Box
        component="span"
        aria-hidden
        sx={{ width: 6, height: 6, borderRadius: "50%", flexShrink: 0, backgroundColor: color }}
      />
      <Box component="span" sx={{ overflow: "hidden", textOverflow: "ellipsis" }}>
        {label}
      </Box>
    </Box>
  );
};

export default StatusChip;
