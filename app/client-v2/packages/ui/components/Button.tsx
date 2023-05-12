// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/no-namespace */

/* eslint-disable @typescript-eslint/ban-types */
import MuiButton from "@mui/material/Button";
import { useCallbackFactory } from "powerhooks/useCallbackFactory";
import { useGuaranteedMemo } from "powerhooks/useGuaranteedMemo";
import type { FC } from "react";
import { forwardRef, memo, useState } from "react";
import * as runExclusive from "run-exclusive";
import { assert } from "tsafe";
import type { Equals } from "tsafe/Equals";
import { capitalize } from "tsafe/capitalize";
import { id } from "tsafe/id";

import { makeStyles } from "../lib/ThemeProvider";
import { breakpointsValues } from "../lib/breakpoints";
import { variantNameUsedForMuiButton } from "../lib/typography";
import { pxToNumber } from "../tools/pxToNumber";
import type { IconProps } from "./Icon";

export type ButtonProps<IconId extends string = never> =
  | ButtonProps.Regular<IconId>
  | ButtonProps.Submit<IconId>;

export namespace ButtonProps {
  type Common<IconId extends string> = {
    className?: string;

    /** Defaults to "primary" */
    variant?: "primary" | "secondary" | "ternary";

    children: React.ReactNode;

    /** Defaults to false */
    disabled?: boolean;

    startIcon?: IconId;
    endIcon?: IconId;

    /** Defaults to false */
    autoFocus?: boolean;

    tabIndex?: number;

    name?: string;
    htmlId?: string;
    "aria-label"?: string;
  };

  export type Regular<IconId extends string = never> = Common<IconId> & {
    onClick?: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
    href?: string;
    /** Default to true if href */
    doOpenNewTabIfHref?: boolean;
  };

  export type Submit<IconId extends string = never> = Common<IconId> & {
    type: "submit";
  };
}

export function createButton<IconId extends string = never>(params?: {
  Icon(props: IconProps<IconId>): ReturnType<FC>;
}) {
  const { Icon } = params ?? {
    Icon: id<(props: IconProps<IconId>) => JSX.Element>(() => <></>),
  };

  const Button = memo(
    forwardRef<HTMLButtonElement, ButtonProps<IconId>>((props, ref) => {
      const {
        className,
        variant = "primary",
        disabled = false,
        children,
        startIcon,
        endIcon,
        autoFocus = false,
        tabIndex,
        name,
        htmlId,
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

      const { classes, cx } = useStyles({
        variant,
        disabled,
        isMouseIn,
      });

      const IconWd = useGuaranteedMemo(
        // eslint-disable-next-line react/display-name
        () => (props: { iconId: IconId }) =>
          <Icon iconId={props.iconId} className={classes.icon} size="default" />,
        [disabled, classes.icon]
      );

      return (
        <MuiButton
          onMouseEnter={handleMousePositionFactory("in")}
          onMouseLeave={handleMousePositionFactory("out")}
          ref={ref}
          className={cx(classes.root, className)}
          //There is an error in @mui/material types, this should be correct.
          disabled={disabled}
          startIcon={startIcon === undefined ? undefined : <IconWd iconId={startIcon} />}
          endIcon={endIcon === undefined ? undefined : <IconWd iconId={endIcon} />}
          autoFocus={autoFocus}
          tabIndex={tabIndex}
          name={name}
          id={htmlId}
          aria-label={ariaLabel}
          {...(() => {
            if ("type" in rest) {
              const { type, ...restRest } = rest;

              //For the forwarding, rest should be empty (typewise),
              assert<Equals<typeof restRest, {}>>();

              return {
                type,
                ...restRest,
              };
            }

            const { onClick, href, doOpenNewTabIfHref = href !== undefined, ...restRest } = rest;

            return {
              onClick,
              href,
              target: doOpenNewTabIfHref ? "_blank" : undefined,
              ...restRest,
            };
          })()}>
          {typeof children === "string" ? capitalize(children) : children}
        </MuiButton>
      );
    })
  );

  const useStyles = makeStyles<{
    variant: NonNullable<ButtonProps["variant"]>;
    disabled: boolean;
    isMouseIn: boolean;
  }>({ name: { Button } })((theme, { variant, disabled, isMouseIn }) => {
    const textColor =
      theme.colors.useCases.typography[
        disabled
          ? "textDisabled"
          : (() => {
              switch (variant) {
                case "primary":
                  return "textFocus";
                case "secondary":
                case "ternary":
                  return "textPrimary";
              }
            })()
      ];

    const hoverTextColor = (() => {
      switch (theme.isDarkModeEnabled) {
        case true:
          return theme.colors.palette[
            (() => {
              switch (variant) {
                case "primary":
                  return "light";
                case "secondary":
                case "ternary":
                  return "dark";
              }
            })()
          ].main;
        case false:
          return theme.colors.palette.light.main;
      }
    })();

    return {
      root: (() => {
        const hoverBackgroundColor =
          theme.colors.useCases.buttons[
            (() => {
              switch (variant) {
                case "primary":
                  return "actionHoverPrimary";
                case "secondary":
                case "ternary":
                  return "actionHoverSecondary";
              }
            })()
          ];

        const paddingSpacingTopBottom = 2;

        const borderWidth = (() => {
          switch (variant) {
            case "primary":
            case "secondary":
              return 2;
            case "ternary":
              return 0;
          }
        })();

        const approxHeight =
          2 * theme.spacing(paddingSpacingTopBottom) +
          2 * borderWidth +
          pxToNumber(theme.typography.variants[variantNameUsedForMuiButton].style.lineHeight);

        return {
          textTransform: "unset" as const,
          backgroundColor: disabled
            ? theme.colors.useCases.buttons.actionDisabledBackground
            : (() => {
                switch (variant) {
                  case "primary":
                  case "secondary":
                    return "transparent";
                  case "ternary":
                    return theme.colors.useCases.surfaces.background;
                }
              })(),
          borderRadius: approxHeight / 2,
          borderWidth,
          borderStyle: "solid",
          borderColor: disabled ? "transparent" : hoverBackgroundColor,
          ...theme.spacing.topBottom("padding", paddingSpacingTopBottom),
          ...theme.spacing.rightLeft(
            "padding",
            (() => {
              if (theme.windowInnerWidth >= breakpointsValues.xl) {
                return 3;
              }

              return 4;
            })()
          ),
          "&.MuiButton-text": {
            color: textColor,
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

          //NOTE WILLIAM: In this example I set the position
          //to relative when the mouse is inside the element.
          //Before it was set when the element was active witch
          //meant that the touch ripple effect would be suddenly
          //interrupted when the mouse button goes up, witch
          //was not very satisfying aesthetic wise.
          //May it also be noted that I have used a parameter instead of
          //:hover, because if we trigger the touch ripple effect and move the
          //mouse outside the element before the effect has had time to
          //finish, it produces the same unsatisfying interruption effect.
          //So I set the parameter using an async function wrapped in
          //a run exclusive, that delays the setting of the position slightly
          //when the mouse moves outside the element.

          position: isMouseIn ? "relative" : "unset",
          "& .MuiTouchRipple-root": {
            display: isMouseIn ? "unset" : "none",
          },
          "&:hover": {
            backgroundColor: hoverBackgroundColor,
            "& .MuiSvgIcon-root": {
              color: hoverTextColor,
            },
            "&.MuiButton-text": {
              color: hoverTextColor,
            },
          },
        } as const;
      })(),
      icon: {
        color: textColor,
      },
    };
  });

  return { Button };
}
