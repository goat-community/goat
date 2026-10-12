"use client";

import { Paper, useTheme } from "@mui/material";
import type { PaperProps } from "@mui/material";
import type { PopperPlacementType } from "@mui/material/Popper";

import { surfaceShadows } from "@/components/dashboard/common/surfaceShadows";
import { HEADER_POPOVER_WIDTH } from "@/components/header/HeaderPopover";

/** Every header popover hangs from the right edge of its trigger, arrow-less. */
export const HEADER_POPOVER_PLACEMENT: PopperPlacementType = "bottom-end";

type Props = Omit<PaperProps, "elevation" | "variant"> & {
  /** CSS width; the default is the one shared by every header popover. */
  width?: string | number;
};

/**
 * The one chrome the header's popovers share (jobs, What's new, the
 * onboarding tray, the account menu): 12px radius, a hairline border, the
 * dashboard's lifted surface shadow and a small gap below the trigger.
 */
const HeaderPopoverPaper = ({ width = HEADER_POPOVER_WIDTH, sx, children, ...rest }: Props) => {
  const theme = useTheme();
  return (
    <Paper
      elevation={0}
      sx={[
        {
          width,
          mt: "6px",
          borderRadius: "12px",
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: surfaceShadows(theme).hover,
          overflow: "hidden",
        },
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
      {...rest}>
      {children}
    </Paper>
  );
};

export default HeaderPopoverPaper;
