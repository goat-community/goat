import type { TooltipProps } from "@mui/material";
import { Tooltip, Typography, type TypographyProps } from "@mui/material";
import type { FC, ReactChild } from "react";
import { useEffect, useRef, useState } from "react";

export interface OverflowTypograpyProps extends TypographyProps {
  children: ReactChild;
  tooltipProps?: Omit<TooltipProps, "title" | "children">;
}

export const OverflowTypograpy: FC<OverflowTypograpyProps> = ({ children, tooltipProps, ...props }) => {
  const ref = useRef<HTMLSpanElement>(null);
  const [tooltipEnabled, setTooltipEnabled] = useState(false);

  useEffect(() => {
    const compareSize = () => {
      if (ref.current) {
        const compare = ref.current.scrollWidth > ref.current.clientWidth;

        setTooltipEnabled(compare);
      }
    };
    compareSize();
    window.addEventListener("resize", compareSize);
    return () => window.removeEventListener("resize", compareSize);
  }, []);

  return (
    <Tooltip title={children} disableHoverListener={!tooltipEnabled} {...tooltipProps}>
      <Typography ref={ref} noWrap overflow="hidden" textOverflow="ellipsis" {...props}>
        {children}
      </Typography>
    </Tooltip>
  );
};
