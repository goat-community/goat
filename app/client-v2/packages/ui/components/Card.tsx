// Copyright (c) 2020 GitHub user u/garronej
import type { ReactNode } from "react";
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../lib/ThemeProvider";

export type CardProps = {
  className?: string;
  aboveDivider?: ReactNode;
  children: ReactNode;
};

export const Card = memo(
  forwardRef<any, CardProps>((props, ref) => {
    const {
      className,
      aboveDivider,
      children,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    return (
      <div ref={ref} className={cx(classes.root, className)} {...rest}>
        {aboveDivider !== undefined && <div className={classes.aboveDivider}>{aboveDivider}</div>}
        <div className={classes.belowDivider}>{children}</div>
      </div>
    );
  })
);

const useStyles = makeStyles({ name: { Card } })((theme) => ({
  root: {
    borderRadius: 4,
    boxShadow: theme.shadows[1],
    backgroundColor: theme.colors.useCases.surfaces.surface1,
    "&:hover": {
      boxShadow: theme.shadows[6],
    },
    display: "flex",
    flexDirection: "column",
  },
  aboveDivider: {
    padding: theme.spacing({ topBottom: 3, rightLeft: 4 }),
    borderBottom: `1px solid ${theme.colors.useCases.typography.textTertiary}`,
    boxSizing: "border-box",
  },
  belowDivider: {
    padding: theme.spacing(4),
    paddingTop: theme.spacing(3),
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
}));
