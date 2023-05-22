// Copyright (c) 2020 GitHub user u/garronej
import { Chip } from "@mui/material";
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";

export type CardProps = {
  className?: string;
  chips: string[];
};

export const ChipList = memo(
  forwardRef<any, CardProps>((props) => {
    const {
      className,
      chips,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    return (
      <div className={cx(classes.chips, className)}>
        {chips.map((chip: string, index: number) => (
          <Chip className={classes.chip} key={index} label={chip} />
        ))}
      </div>
    );
  })
);

const useStyles = makeStyles({ name: { ChipList } })((theme) => ({
  chips: {
    display: "flex",
    paddingBottom: "4px",
    width: "100%",
    overflowX: "auto",
    overflowY: "hidden",
    scrollbarWidth: "thin",
    scrollbarColor: "transparent transparent",
    "&::-webkit-scrollbar": {
      height: "4px",
    },
    "&::-webkit-scrollbar-thumb": {
      backgroundColor: theme.colors.useCases.surfaces.background,
    },
    "&::-moz-scrollbar": {
      width: "4px",
    },
    "&::-moz-scrollbar-thumb": {
      backgroundColor: theme.colors.useCases.surfaces.background,
    },
    "&::-ms-scrollbar": {
      height: "4px",
    },
    "&::-ms-scrollbar-thumb": {
      backgroundColor: theme.colors.useCases.surfaces.background,
    },
    borderRadius: "20pxpx",
  },
  chip: {
    backgroundColor: theme.colors.useCases.surfaces.background,
    marginRight: "8px",
    padding: "7px 6px",
  },
}));
