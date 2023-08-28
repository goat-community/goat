// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable react/display-name */
import MuiTooltip from "@mui/material/Tooltip";
import { memo } from "react";
import type { ReactNode, ReactElement } from "react";

import { makeStyles } from "../../lib/ThemeProvider";
import { Text } from "../theme";

export type TooltipProps = {
  title: NonNullable<ReactNode> | undefined;
  children: ReactElement;
  enterDelay?: number;
};

export const Tooltip = memo((props: TooltipProps) => {
  const { title, children, enterDelay } = props;

  const { classes } = useStyles();

  if (title === undefined) {
    return children;
  }

  return (
    <MuiTooltip
      title={
        <Text className={classes.root} typo="caption">
          {title}
        </Text>
      }
      enterDelay={enterDelay}>
      {children}
    </MuiTooltip>
  );
});

const useStyles = makeStyles({ name: { Tooltip } })((theme) => ({
  root: {
    color: theme.colors.palette.light.light,
  },
}));
