import { Chip } from "@mui/material";
import { forwardRef, memo, useEffect, useRef } from "react";

import { makeStyles } from "../../lib/ThemeProvider";
import { Text } from "../theme";

export type ChipListProps = {
  className?: string;
  chips: string[];
};

export const ChipList = memo(
  forwardRef<any, ChipListProps>((props, ref) => {
    const { className, chips } = props;
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

    const { classes, cx } = useStyles();

    return (
      <div className={className} ref={containerRef} style={{ overflowX: "auto" }}>
        <div style={{ display: "flex" }} className={classes.chips}>
          {chips.map((chip: string, index: number) => (
            <Chip key={index} label={<Text typo="body 3">{chip}</Text>} className={classes.chip} />
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
    padding: "7px 6px",
    fontStyle: "italic",
    fontSize: "11px",
  },
}));

export default ChipList;
