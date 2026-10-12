"use client";

import { Box, Button, ButtonBase, Typography, alpha, useMediaQuery, useTheme } from "@mui/material";
import type { SxProps, Theme } from "@mui/material";
import type { ReactNode } from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import type { SupportCategory } from "@/lib/validations/support";

/** The support pages' one mobile/desktop split — the same `md` breakpoint the Content page uses.
 * The pages render in the browser only, so the query is answered on the first render (`noSsr`)
 * instead of one frame later: a phone never flashes the desktop layout. */
export const useSupportMobile = (): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.down("md"), { noSsr: true });
};

/** The page measure and padding Content and Catalog use: the `xl` width, 40px
 * around on desktop, 16px/14px on a phone. */
export const SupportPage = ({
  mobile,
  maxWidth,
  children,
}: {
  mobile: boolean;
  /** A narrower, centred column for a single form (content width, padding excluded). */
  maxWidth?: number;
  children: ReactNode;
}) => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        width: "100%",
        maxWidth: maxWidth ? maxWidth + 80 : theme.breakpoints.values.xl,
        mx: "auto",
        boxSizing: "border-box",
        padding: mobile ? "16px 14px 40px" : "40px",
      }}>
      {children}
    </Box>
  );
};

/** "‹ Support": the text link back to the ticket list, styled like the catalog
 * detail pages' back link. */
export const BackLink = ({
  label,
  onClick,
  disabled,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) => (
  <Button
    variant="text"
    size="small"
    onClick={onClick}
    disabled={disabled}
    startIcon={<Icon iconName={ICON_NAME.CHEVRON_LEFT} style={{ fontSize: 12 }} htmlColor="inherit" />}
    sx={{
      ml: "-6px",
      px: "6px",
      minWidth: 0,
      fontSize: 14,
      fontWeight: 600,
      textTransform: "none",
      "& .MuiButton-startIcon": { mr: "6px" },
    }}>
    {label}
  </Button>
);

/** The small uppercase heading of a side-panel card, as the Content details panel draws its sections. */
export const RailLabel = ({ children, sx }: { children: ReactNode; sx?: SxProps<Theme> }) => (
  <Typography
    component="div"
    sx={[
      {
        fontSize: 11,
        fontWeight: 800,
        letterSpacing: "0.7px",
        textTransform: "uppercase",
        color: "text.secondary",
        mb: "10px",
      },
      ...(Array.isArray(sx) ? sx : [sx]),
    ]}>
    {children}
  </Typography>
);

export const CATEGORY_ICON: Record<SupportCategory, ICON_NAME> = {
  bug: ICON_NAME.BUG,
  how_to: ICON_NAME.BOOK,
  data_issue: ICON_NAME.DATABASE,
  feature_request: ICON_NAME.STAR,
  account_billing: ICON_NAME.CREDIT_CARD,
  other: ICON_NAME.COMMENT,
};

/** A ticket's category as the tinted square a list row leads with (the
 * dashboard's `MarkBlock` shape); a closed ticket's mark is greyed out. */
export const CategoryMark = ({
  category,
  muted,
  size = 34,
}: {
  category: SupportCategory;
  muted?: boolean;
  size?: number;
}) => {
  const theme = useTheme();
  const color = muted ? theme.palette.text.secondary : theme.palette.primary.main;
  return (
    <Box
      sx={{
        width: size,
        height: size,
        flexShrink: 0,
        borderRadius: `${Math.round(size / 4)}px`,
        backgroundColor: muted ? theme.palette.action.hover : alpha(color, 0.12),
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}>
      <Icon
        iconName={CATEGORY_ICON[category]}
        style={{ fontSize: Math.round(size * 0.45) }}
        htmlColor={color}
      />
    </Box>
  );
};

export type SegmentOption<V extends string> = { value: V; label: string; icon: ICON_NAME };

/** Two or more segments in one pill, the active one filled with the primary
 * tint — `LayoutToggle`'s look for a choice that is not Grid/List. */
export const SegmentedToggle = <V extends string>({
  value,
  options,
  onChange,
  fullWidth,
}: {
  value: V;
  options: SegmentOption<V>[];
  onChange: (value: V) => void;
  /** Phone layout: the pill spans the row and the segments share it equally. */
  fullWidth?: boolean;
}) => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        display: fullWidth ? "grid" : "flex",
        gridTemplateColumns: fullWidth ? `repeat(${options.length}, minmax(0, 1fr))` : undefined,
        gap: "2px",
        padding: "3px",
        flexShrink: 0,
        borderRadius: "999px",
        border: `1px solid ${theme.palette.divider}`,
        backgroundColor: theme.palette.background.paper,
      }}>
      {options.map((option) => {
        const on = option.value === value;
        return (
          <ButtonBase
            key={option.value}
            aria-pressed={on}
            onClick={() => onChange(option.value)}
            sx={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
              height: 30,
              px: "13px",
              minWidth: 0,
              borderRadius: "999px",
              backgroundColor: on ? alpha(theme.palette.primary.main, 0.12) : "transparent",
              color: on ? theme.palette.primary.main : theme.palette.text.secondary,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              whiteSpace: "nowrap",
            }}>
            <Icon
              iconName={option.icon}
              style={{ fontSize: 13 }}
              htmlColor={on ? theme.palette.primary.main : theme.palette.text.secondary}
            />
            {option.label}
          </ButtonBase>
        );
      })}
    </Box>
  );
};

/** A soft, rounded one-line notice (a tinted strip rather than a full alert) for
 * banners that sit inside a card. */
export const InlineNotice = ({
  icon,
  tone,
  children,
}: {
  icon: ICON_NAME;
  tone: "warning" | "neutral";
  children: ReactNode;
}) => {
  const theme = useTheme();
  const color = tone === "warning" ? theme.palette.warning.main : theme.palette.text.secondary;
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        px: "16px",
        py: "10px",
        fontSize: 13,
        lineHeight: 1.45,
        color: theme.palette.text.primary,
        backgroundColor: tone === "warning" ? alpha(color, 0.12) : theme.palette.action.hover,
        borderBottom: `1px solid ${tone === "warning" ? alpha(color, 0.3) : theme.palette.divider}`,
      }}>
      <Icon iconName={icon} style={{ fontSize: 13, flexShrink: 0 }} htmlColor={color} />
      <Box component="span" sx={{ minWidth: 0 }}>
        {children}
      </Box>
    </Box>
  );
};
