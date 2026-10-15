"use client";

import { Button, IconButton, Tooltip, alpha, useTheme } from "@mui/material";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { setDockState, useDockState } from "@/lib/assistant/store";

import { accentSoft, accentText, focusRing } from "@/components/assistant/styles";

/**
 * "Ask AI" in the top bar (spec §10); absent wherever the dock is not available.
 * `compact` shows the icon alone, for narrow headers. Closed, it is an outlined
 * 32px pill like the header's onboarding pill; open, it takes the primary tint.
 * Only colours change, so the header does not shift when it toggles.
 */
export default function AskAiButton({ compact = false }: { compact?: boolean }) {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const dock = useDockState();
  if (!dock.enabled) return null;
  const toggle = () => setDockState({ open: !dock.open });
  const sx = {
    height: 32,
    flexShrink: 0,
    border: `1px solid ${dock.open ? theme.palette.primary.main : theme.palette.divider}`,
    color: dock.open ? accentText(theme) : theme.palette.text.primary,
    bgcolor: dock.open ? accentSoft(theme) : "transparent",
    transition: theme.transitions.create(["background-color", "border-color", "color"], { duration: 120 }),
    "&:hover": {
      bgcolor: dock.open ? alpha(theme.palette.primary.main, 0.18) : theme.palette.action.hover,
      borderColor: dock.open ? theme.palette.primary.main : alpha(theme.palette.text.primary, 0.24),
    },
    ...focusRing(theme),
  };
  const icon = (
    <Icon
      iconName={ICON_NAME.SPARKLES}
      style={{ fontSize: 16, color: dock.open ? "inherit" : theme.palette.primary.main }}
    />
  );
  if (compact) {
    return (
      <Tooltip title={t("assistant_ask_ai")}>
        <IconButton
          size="small"
          aria-label={t("assistant_ask_ai")}
          aria-pressed={dock.open}
          onClick={toggle}
          sx={{ ...sx, width: 32, borderRadius: "50%" }}>
          {icon}
        </IconButton>
      </Tooltip>
    );
  }
  return (
    <Button
      size="small"
      variant="text"
      aria-pressed={dock.open}
      onClick={toggle}
      startIcon={icon}
      sx={{
        ...sx,
        "&&": { px: "12px", py: 0 },
        "& .MuiButton-startIcon": { ml: 0, mr: "7px" },
        borderRadius: "999px",
        textTransform: "none",
        fontSize: 13,
        fontWeight: 700,
        letterSpacing: "0.1px",
        whiteSpace: "nowrap",
      }}>
      {t("assistant_ask_ai")}
    </Button>
  );
}
