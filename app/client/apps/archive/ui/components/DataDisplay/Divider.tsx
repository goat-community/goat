// Copyright (c) 2020 GitHub user u/garronej
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";

export type DividerProps = {
  className?: string;
  width: string;
  color: "main" | "light" | "gray";
  lineColor?: string;
};

export const Divider = memo(
  forwardRef<any, DividerProps>((props) => {
    const {
      className,
      width,
      color,
      lineColor,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    return (
      <>
        <div
          className={cx(classes.root, classes[color], className)}
          style={{ width: width, backgroundColor: lineColor }}
        />
      </>
    );
  })
);

const useStyles = makeStyles({ name: { Divider } })((theme) => ({
  root: {
    height: "1px",
    opacity: "0.08",
    margin: "16px 0",
  },
  main: {
    backgroundColor: theme.isDarkModeEnabled
      ? theme.colors.palette.light.main
      : theme.colors.palette.dark.main,
  },
  light: {
    backgroundColor: theme.isDarkModeEnabled
      ? theme.colors.palette.light.light
      : theme.colors.palette.dark.light,
  },
  gray: {
    backgroundColor: theme.isDarkModeEnabled
      ? theme.colors.palette.light.greyVariant1
      : theme.colors.palette.dark.greyVariant1,
  },
}));
