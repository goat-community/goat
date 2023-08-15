// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable react/display-name */
import MuiCircularProgress from "@mui/material/CircularProgress";
import { memo } from "react";

import { makeStyles } from "../lib/ThemeProvider";

export type CircularProgressProps = {
  className?: string;
  size?: number;
  color?: "primary" | "textPrimary";
};

export const CircularProgress = memo((props: CircularProgressProps) => {
  const { className, size = 40, color = "primary" } = props;

  const { classes, cx } = useStyles({ color });

  return (
    <MuiCircularProgress
      color={color === "textPrimary" ? undefined : color}
      className={cx(classes.root, className)}
      size={size}
    />
  );
});

const useStyles = makeStyles<Pick<Required<CircularProgressProps>, "color">>({
  name: { CircularProgress },
})((theme, { color }) => ({
  root: {
    color: color !== "textPrimary" ? undefined : theme.colors.useCases.typography.textPrimary,
  },
}));
