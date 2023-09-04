import { Chip as MUIChip } from "@mui/material";
import React from "react";

import { changeColorOpacity } from "@/lib/utils/helpers";
import { makeStyles } from "@/lib/theme";
import { Text } from "@/lib/theme";
// import type { IconId } from "../theme";
import { Icon } from "@p4b/ui/components/Icon";
import type { ICON_NAME } from "@p4b/ui/components/Icon";
import { useTheme } from "@/lib/theme";

interface ChipProps {
  className?: string;
  variant?: "filled" | "Border" | "filledWithBorder";
  textDesign?: "normal" | "italic";
  color?: "dark" | "focus" | "orangeWarning" | "redError";
  label: React.ReactNode; // JSX Element
  icon?: ICON_NAME;
}

export const Chip = (props: ChipProps) => {
  const { variant = "filled", textDesign = "normal", label, className, color = "dark", icon } = props;

  const { classes, cx } = useStyles({ variant, textDesign, color, icon });

  const theme = useTheme()
  const labelChip = (
    <div className={classes.chipContent}>
      {icon ? <Icon iconName={icon} htmlColor={`${theme.colors.palette[color].main}BF`} fontSize="small"/> : null}
      <Text className={classes.chipText} typo="body 3">
        {label}
      </Text>
    </div>
  );

  return <MUIChip className={cx(classes.chip, className)} label={labelChip} />;
};

const useStyles = makeStyles<{
  variant: "filled" | "Border" | "filledWithBorder";
  textDesign: "normal" | "italic";
  color: "dark" | "focus" | "orangeWarning" | "redError";
  icon?: ICON_NAME;
}>({ name: { Chip } })((theme, { variant, textDesign, color, icon }) => {
  let bgColor;
  switch (variant) {
    case "filled":
    case "filledWithBorder":
      bgColor = changeColorOpacity({
        color: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant2,
        opacity: 0.3,
      });
      break;
    case "Border":
      bgColor = "transparent";
      break;
  }

  let border;
  switch (variant) {
    case "filled":
      border = "none";
      break;
    case "filledWithBorder":
    case "Border":
      switch (color) {
        case "dark":
          border = `1px solid ${theme.colors.palette.dark.main}BF`;
          break;
        case "focus":
          border = `1px solid ${theme.colors.palette.focus.main}BF`;
          break;
        case "orangeWarning":
          border = `1px solid ${theme.colors.palette.orangeWarning.main}BF`;
          break;
        case "redError":
          border = `1px solid ${theme.colors.palette.redError.main}BF`;
          break;
      }
      break;
  }

  let textColor;
  switch (color) {
    case "dark":
      textColor = theme.colors.palette.dark.main;
      break;
    case "focus":
      textColor = theme.colors.palette.focus.main;
      break;
    case "orangeWarning":
      textColor = theme.colors.palette.orangeWarning.main;
      break;
    case "redError":
      textColor = theme.colors.palette.redError.main;
      break;
  }

  return {
    chip: {
      backgroundColor: bgColor,
      border: border,
      fontStyle: textDesign === "italic" ? "italic" : "normal",
    },
    chipContent: {
      display: "flex",
      alignItems: "center",
      gap: "6px",
      paddingRight: icon ? "6px" : "0px",
    },
    chipText: {
      color: textColor,
      fontStyle: "italic",
    },
  };
});
