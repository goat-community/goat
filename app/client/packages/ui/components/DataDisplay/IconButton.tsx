"use client";

// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/no-namespace */

/* eslint-disable @typescript-eslint/ban-types */
import MuiIconButton from "@mui/material/IconButton";
import { useCallbackFactory } from "powerhooks/useCallbackFactory";
import { useState } from "react";
import type { FC } from "react";
import { forwardRef, memo } from "react";
import * as runExclusive from "run-exclusive";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";
import { id } from "tsafe/id";

import { makeStyles } from "../../lib/ThemeProvider";
import type { IconProps } from "./Icon";

export type IconButtonProps<IconId extends string = never> =
  | IconButtonProps.Clickable<IconId>
  | IconButtonProps.Link<IconId>
  | IconButtonProps.Submit<IconId>;

export namespace IconButtonProps {
  type Common<IconId extends string> = {
    className?: string;
    iconClassName?: string;
    iconId: IconId;
    size?: IconProps["size"];
    /** Defaults to false */
    disabled?: boolean;

    /** Defaults to false */
    autoFocus?: boolean;

    tabIndex?: number;

    /** Defaults to grey */
    iconVariant?: "white" | "secondary" | "focus" | "grey" | "grey2" | "error";
    name?: string;
    id?: string;
    "aria-label"?: string;
  };

  export type Clickable<IconId extends string = never> = Common<IconId> & {
    onClick: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
    href?: string;
  };

  export type Link<IconId extends string = never> = Common<IconId> & {
    href: string;
    /** Defaults to true */
    doOpenNewTabIfHref?: boolean;
  };

  export type Submit<IconId extends string = never> = Common<IconId> & {
    type: "submit";
  };
}

export function createIconButton<IconId extends string = never>(params?: {
  Icon(props: IconProps<IconId>): ReturnType<FC>;
}) {
  const { Icon } = params ?? {
    Icon: id<(props: IconProps<IconId>) => JSX.Element>(() => <></>),
  };

  const IconButton = memo(
    forwardRef<HTMLButtonElement, IconButtonProps<IconId>>((props, ref) => {
      const {
        className,
        iconClassName,
        iconId,
        size,
        disabled = false,
        autoFocus = false,
        tabIndex,
        iconVariant = "grey2",
        name,
        id,
        "aria-label": ariaLabel,
        //For the forwarding, rest should be empty (typewise)
        ...rest
      } = props;

      const [isMouseIn, setIsMouseIn] = useState(false);

      const handleMousePositionFactory = useCallbackFactory(
        runExclusive.build(async ([position]: ["in" | "out"]) => {
          switch (position) {
            case "in":
              setIsMouseIn(true);
              return;
            case "out":
              await new Promise<void>((resolve) => setTimeout(resolve, 400));
              setIsMouseIn(false);
          }
        })
      );

      const { classes, cx } = useStyles({ disabled, isMouseIn, iconVariant });

      return (
        <MuiIconButton
          onMouseEnter={handleMousePositionFactory("in")}
          onMouseLeave={handleMousePositionFactory("out")}
          ref={ref}
          className={cx(classes.root, className)}
          disabled={disabled}
          aria-label={ariaLabel ?? undefined}
          autoFocus={autoFocus}
          tabIndex={tabIndex}
          name={name}
          id={id}
          {...(() => {
            if ("onClick" in rest) {
              const { onClick, href, ...restRest } = rest;

              //For the forwarding, rest should be empty (typewise),
              assert<Equals<typeof restRest, {}>>();

              return { onClick, href, ...restRest };
            }

            if ("href" in rest) {
              const { href, doOpenNewTabIfHref = true, ...restRest } = rest;

              //For the forwarding, rest should be empty (typewise),
              assert<Equals<typeof restRest, {}>>();

              return {
                href,
                target: doOpenNewTabIfHref ? "_blank" : undefined,
                ...restRest,
              };
            }

            if ("type" in rest) {
              const { type, ...restRest } = rest;

              //For the forwarding, rest should be empty (typewise),
              assert<Equals<typeof restRest, {}>>();

              return {
                type,
                ...restRest,
              };
            }
          })()}>
          <Icon iconId={iconId} className={cx(classes.icon, iconClassName)} size={size} />
        </MuiIconButton>
      );
    })
  );

  const useStyles = makeStyles<{
    disabled: boolean;
    isMouseIn: boolean;
    iconVariant: "white" | "secondary" | "focus" | "grey" | "grey2" | "error";
  }>({
    name: { IconButton },
  })((theme, { isMouseIn, iconVariant }) => {
    let color;
    let hoverColor;
    switch (iconVariant) {
      case "focus":
        color = theme.colors.palette.focus.main;
        hoverColor = theme.colors.palette.focus.light;
        break;
      case "secondary":
        color = theme.colors.palette.light.main;
        hoverColor = theme.colors.palette.light.light;
        break;
      case "grey":
        color = theme.colors.palette.light.greyVariant4;
        hoverColor = theme.colors.palette.light.greyVariant3;
        break;
      case "grey2":
        color = theme.colors.palette.light.greyVariant2;
        hoverColor = theme.colors.palette.light.greyVariant3;
        break;
      case "white":
        color = theme.colors.palette.light.main;
        hoverColor = theme.colors.palette.light.light;
        break;
      case "error":
        color = theme.colors.palette.redError.main;
        hoverColor = `${theme.colors.palette.redError.main}80`;
        break;
      default:
        color = "light";
        break;
    }

    return {
      root: {
        padding: theme.spacing(2),
        "&:hover": {
          backgroundColor: "unset",
          "& svg": {
            color: hoverColor,
          },
        },

        //NOTE: If the position of the button is relative (the default)
        //it goes hover everything not positioned, we have to mess with z-index and
        //we don't want that.
        //The relative positioning is needed for the touch ripple effect.
        //If we dont have position relative the effect is not restricted to the
        //button: https://user-images.githubusercontent.com/6702424/157982515-c97dfa81-b09a-4323-beb9-d1e92e7ebe4d.mov
        //The solution is set 'position: relative' only when the ripple effect is supposed to be visible.
        //This explain the following awful rules.
        //The expected result is: https://user-images.githubusercontent.com/6702424/157984062-27e544c3-f86f-47b8-b141-c5f61b8a2880.mov
        position: isMouseIn ? "relative" : "unset",
        "& .MuiTouchRipple-root": {
          display: isMouseIn ? "unset" : "none",
        },
      },
      icon: {
        color: color,
        "&:hover": {
          color: hoverColor,
        },
      },
    };
  });

  return { IconButton };
}
