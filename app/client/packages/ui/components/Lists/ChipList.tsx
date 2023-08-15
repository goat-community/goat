"use client";

import { Chip } from "@mui/material";
import { forwardRef, memo, useEffect, useRef } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../../lib/ThemeProvider";
import { Text } from "../theme";

export type ChipListProps = {
  className?: string;
  chips: string[];
};

/**
 * A memoized functional component that renders a list of chips.
 * @param {ChipListProps} props - The component props.
 * @param {React.Ref<any>} ref - The ref object for the component.
 * @returns The rendered component.
 */
export const ChipList = memo(
  forwardRef<any, ChipListProps>((props) => {
    const { className, chips } = props;

    const { classes } = useStyles();

    // refs
    const containerRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
      const handleOverflow = () => {
        const container = containerRef.current;
        if (!container) return;

        const containerRect = container.getBoundingClientRect();
        const chipsContainer = container.firstChild as HTMLElement;

        if (chipsContainer) {
          const chips = Array.from(chipsContainer.children) as HTMLElement[];

          chips.forEach((chip) => {
            const chipRect = chip.getBoundingClientRect();
            const isChipFullyVisible =
              chipRect.left >= containerRect.left && chipRect.right <= containerRect.right;

            chip.style.display = isChipFullyVisible ? "flex" : "none";
          });
        }
      };

      handleOverflow();

      window.addEventListener("resize", handleOverflow);

      return () => {
        window.removeEventListener("resize", handleOverflow);
      };
    }, []);

    return (
      <div className={className} ref={containerRef} style={{ overflowX: "auto" }}>
        <div style={{ display: "flex" }} className={classes.chips}>
          {chips.map((chip: string) => (
            <Chip key={v4()} label={<Text typo="body 3">{chip}</Text>} className={classes.chip} />
          ))}
          <Chip label="..." className={classes.chip} />
        </div>
      </div>
    );
  })
);

function blendHexColorWithOpacity(hexColor: string, opacity: number) {
  // Remove the '#' character from the hex color
  const normalizedHexColor = hexColor.replace("#", "");

  // Convert the opacity to its hexadecimal equivalent
  const opacityHex = Math.round(opacity * 255)
    .toString(16)
    .padStart(2, "0");

  // Combine the opacity hex value with the original hex color
  const blendedHexColor = `#${normalizedHexColor}${opacityHex}`;

  return blendedHexColor;
}

const useStyles = makeStyles({ name: { ChipList } })((theme) => ({
  chips: {
    display: "flex",
    width: "100%",
  },
  chip: {
    backgroundColor: blendHexColorWithOpacity(
      theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant2,
      0.3
    ),
    marginRight: "8px",
    padding: "7px 18px",
    fontStyle: "italic",
    fontSize: "11px",
    "& .mui-6od3lo-MuiChip-label": {
      padding: "0",
    },
  },
}));

export default ChipList;
