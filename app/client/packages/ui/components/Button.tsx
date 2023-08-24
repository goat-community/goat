"use client";

// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/no-namespace */

/* eslint-disable @typescript-eslint/ban-types */
import { LoadingButton } from "@mui/lab";
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
import { variantNameUsedForMuiButton } from "../lib/typography";
import { pxToNumber } from "../tools/pxToNumber";
import type { IconProps } from "./DataDisplay";

export type ButtonProps<IconId extends string = never> =
  | ButtonProps.Regular<IconId>
  | ButtonProps.Submit<IconId>;

export namespace ButtonProps {
  type Common<IconId extends string> = {
    className?: string;

    /** Defaults to "primary" */
    variant?: "primary" | "secondary" | "ternary" | "warning" | "noBorder";

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
    loading?: boolean;
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
        loading,
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
          <Icon iconId={props.iconId} className={classes.icon} size="small" />,
        [disabled, classes.icon]
      );

      return (
        <>
          {loading ? (
            <LoadingButton
              loading={loading}
              loadingPosition="center"
              className={cx(classes.root, className)}
            />
          ) : (
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
          )}
        </>
      );
    })
  );

  const useStyles = makeStyles<{
    variant: NonNullable<ButtonProps["variant"]>;
    disabled: boolean;
    isMouseIn: boolean;
  }>({ name: { Button } })((theme, { variant, disabled, isMouseIn }) => {
    const textColor = disabled
      ? theme.colors.useCases.typography["textDisabled"]
      : (() => {
        switch (variant) {
          case "primary":
            return theme.colors.useCases.typography["textFocus"];
          case "secondary":
            return theme.colors.useCases.typography["textPrimary"];
          case "ternary":
            return theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].main;
          case "noBorder":
            return `${theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].greyVariant3}E6`;
          case "warning":
            return theme.muiTheme.palette.warning.main;
        }
      })();

    const hoverTextColor = (() => {
      switch (variant) {
        case "primary":
          return theme.colors.palette["light"].main;
        case "secondary":
          return theme.colors.palette["light"].main;
        case "ternary":
          return theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].main;
        case "noBorder":
          return theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].main;
        case "warning":
          return theme.muiTheme.palette.warning.light;
      }
    })();

    return {
      root: (() => {
        const hoverBackgroundColor = (() => {
          switch (variant) {
            case "primary":
              return theme.colors.useCases.buttons["actionHoverPrimary"];
            case "secondary":
              return theme.colors.useCases.buttons["actionHoverSecondary"];
            case "ternary":
              return theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].main;
            case "noBorder":
              return `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}80`;
            case "warning":
              return theme.muiTheme.palette.warning.main;
          }
        })();

        const paddingSpacingTopBottom = 2;

        const borderWidth = (() => {
          switch (variant) {
            case "primary":
            case "secondary":
              return 1;
            case "ternary":
            case "noBorder":
              return 0;
            default:
              return 1;
          }
        })();

        const approxHeight =
          2 * theme.spacing(paddingSpacingTopBottom) +
          2 * borderWidth +
          pxToNumber(theme.typography.variants[variantNameUsedForMuiButton].style.lineHeight);

        return {
          fontWeight: "500",
          fontSize: "14px",
          textTransform: "unset" as const,
          backgroundColor: (() => {
            switch (variant) {
              case "noBorder":
                return "transparent";
                break;
              case "primary":
              case "secondary":
              case "warning":
                if (disabled) {
                  theme.colors.useCases.buttons.actionDisabledBackground;
                } else {
                  return "transparent";
                }
              case "ternary":
                if (disabled) {
                  theme.colors.useCases.buttons.actionDisabledBackground;
                } else {
                  return theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].main;
                }
            }
          })(),
          borderRadius: variant === "noBorder" ? "1px" : approxHeight / 2,
          borderWidth,
          borderStyle: "solid",
          borderColor: disabled ? "transparent" : hoverBackgroundColor,
          ...theme.spacing.topBottom("padding", paddingSpacingTopBottom),
          ...theme.spacing.rightLeft(
            "padding",
            (() => {
              if (variant === "noBorder") {
                return 1;
              }

              return 4;
            })()
          ),
          "&.MuiButton-text": {
            color: textColor,
          },
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
