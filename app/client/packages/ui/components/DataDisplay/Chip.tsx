import { Chip as MUIChip } from "@mui/material";
import React from "react";

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";
import { Icon, Text } from "../theme";
import type { IconId } from "../theme";

interface ChipProps {
  className?: string;
  variant?: "filled" | "Border" | "filledWithBorder";
  textDesign?: "normal" | "italic";
  color?: "main" | "success" | "warning" | "error";
  label: React.ReactNode; // JSX Element
  icon?: IconId;
}

export const Chip = (props: ChipProps) => {
  const { variant = "filled", textDesign = "normal", label, className, color = "main", icon } = props;

  const { classes, cx } = useStyles({ variant, textDesign, color, icon });

  const labelChip = (
    <div className={classes.chipContent}>
      {icon ? <Icon iconId={icon} iconVariant={color} /> : null}
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
  color: "main" | "success" | "warning" | "error";
  icon?: IconId;
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
        case "main":
          border = `1px solid ${theme.colors.palette.dark.main}BF`;
          break;
        case "success":
          border = `1px solid ${theme.colors.palette.greenSuccess.main}BF`;
          break;
        case "warning":
          border = `1px solid ${theme.colors.palette.orangeWarning.main}BF`;
          break;
        case "error":
          border = `1px solid ${theme.colors.palette.redError.main}BF`;
          break;
      }
      break;
  }

  let textColor;
  switch (color) {
    case "main":
      textColor = theme.colors.palette.dark.main;
      break;
    case "success":
      textColor = theme.colors.palette.greenSuccess.main;
      break;
    case "warning":
      textColor = theme.colors.palette.orangeWarning.main;
      break;
    case "error":
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
