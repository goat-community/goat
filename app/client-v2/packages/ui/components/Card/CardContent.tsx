// Copyright (c) 2020 GitHub user u/garronej
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";
import { Icon } from "../Icon/IconBase";
import { ChipList } from "../Lists/ChipList";
import { Text } from "../Text/TextBase";

export type CardContentProps<IconId extends string> = {
  className?: string;
  title: string;
  description?: string;
  chips: string[];
  info?: {
    author: string;
    date: string;
  };
  icon?: IconId;
};

export const CardContent = memo(
  forwardRef<any, CardContentProps<"home" | "help" | "file">>((props) => {
    const {
      className,
      title,
      description,
      chips,
      info,
      icon,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    return (
      <div className={cx(className, classes.wrapper)}>
        {info ? (
          <Text typo="body 2">
            {info.author} • {info.date}
          </Text>
        ) : null}
        <div className={classes.iconTitle}>
          {icon ? (
            <div className={classes.icon}>
              <Icon className={classes.iconSize} iconId={icon} />
            </div>
          ) : null}
          <Text typo="body 1">{title}</Text>
        </div>
        {description ? (
          <Text typo="body 2" className={classes.description}>
            {description}
          </Text>
        ) : null}
        <ChipList chips={chips} />
      </div>
    );
  })
);

const useStyles = makeStyles({ name: { CardContent } })((theme) => ({
  icon: {
    padding: "5px 7px",
    background: theme.colors.useCases.surfaces.background,
    width: "fit-content",
    borderRadius: 4,
    marginRight: "8px",
  },
  iconTitle: {
    display: "flex",
    margin: "4px",
    marginBottom: "8px",
    alignItems: "center",
  },
  iconSize: {
    width: "20px",
    height: "26.66px",
  },
  description: {
    paddingBottom: "16px",
  },
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
  wrapper: {
    padding: theme.spacing(4),
    paddingTop: theme.spacing(3),
  },
}));
