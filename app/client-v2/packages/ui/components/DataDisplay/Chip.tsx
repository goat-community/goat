import { Chip as MUIChip } from "@mui/material";
import React from "react";

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";

interface ChipProps {
  variant: "filled" | "Border" | "filledWithBorder";
  textDesign: "normal" | "italic";
  label: React.ReactNode;
}

export const Chip = (props: ChipProps) => {
  const { variant = "filled", textDesign = "normal", label } = props;

  const { classes } = useStyles({ variant, textDesign });

  return <MUIChip className={classes.chip} label={label} />;
};

const useStyles = makeStyles<{
  variant: "filled" | "Border" | "filledWithBorder";
  textDesign: "normal" | "italic";
}>({ name: { Chip } })((theme, { variant, textDesign }) => {
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
      border = `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant3}`;
      break;
  }

  return {
    chip: {
      backgroundColor: bgColor,
      border: border,
      fontStyle: textDesign === "italic" ? "italic" : "normal",
    },
  };
});
