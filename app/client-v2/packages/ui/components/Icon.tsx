// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/ban-types */
import SvgIcon from "@mui/material/SvgIcon";
import { memo, forwardRef } from "react";
import type { ForwardedRef, MouseEventHandler, ElementType } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../lib/ThemeProvider";
import type { IconSizeName } from "../lib/icon";

/**
 * Size:
 *
 * If you want to change the size of the icon you can set the font
 * size manually with css using one of the typography
 * fontSize of the root in px.
 *
 * If you place it inside a <Text> element you can define it's size proportional
 * to the font-height:
 * {
 *     "fontHeight": "inherit",
 *     ...(()=>{
 *         const factor = 1.3;
 *         return { "width": `${factor}em`, "height": `${factor}em` }
 *     })()
 * }
 *
 * Color:
 *
 * By default icons inherit the color.
 * If you want to change the color you can
 * simply set the style "color".
 *
 */
export type IconProps<IconId extends string = string> = {
  iconId: IconId;
  className?: string;
  /** default default */
  size?: IconSizeName;
  onClick?: MouseEventHandler<SVGSVGElement>;
};

export type MuiIconLike = (props: {
  ref: ForwardedRef<SVGSVGElement>;
  className: string;
  onClick?: MouseEventHandler<SVGSVGElement>;
}) => JSX.Element;

export type SvgComponentLike = ElementType;

function isMuiIcon(Component: MuiIconLike | SvgComponentLike): Component is MuiIconLike {
  return "type" in (Component as MuiIconLike);
}

export function createIcon<IconId extends string>(componentByIconId: {
  readonly [iconId in IconId]: MuiIconLike | SvgComponentLike;
}) {
  const useStyles = makeStyles<{ size: IconSizeName }>()((theme, { size }) => ({
    root: {
      color: theme.colors.palette.dark.greyVariant4,
      // https://stackoverflow.com/a/24626986/3731798
      //"verticalAlign": "top",
      //"display": "inline-block"
      verticalAlign: "top",
      fontSize: theme.iconSizesInPxByName[size],
      width: "1em",
      height: "1em",
    },
  }));

  const Icon = memo(
    forwardRef<SVGSVGElement, IconProps<IconId>>((props, ref) => {
      const { iconId, className, size = "default", onClick, ...rest } = props;

      //For the forwarding, rest should be empty (typewise),
      assert<Equals<typeof rest, {}>>();

      const { classes, cx } = useStyles({ size });

      const Component: MuiIconLike | SvgComponentLike = componentByIconId[iconId];

      return isMuiIcon(Component) ? (
        <Component ref={ref} className={cx(classes.root, className)} onClick={onClick} {...rest} />
      ) : (
        <SvgIcon
          ref={ref}
          onClick={onClick}
          className={cx(classes.root, className)}
          component={Component}
          {...rest}
        />
      );
    })
  );

  return { Icon };
}

/*
NOTES:
https://github.com/mui-org/material-ui/blob/e724d98eba018e55e1a684236a2037e24bcf050c/packages/material-ui/src/styles/createTypography.js#L45
https://github.com/mui-org/material-ui/blob/53a1655143aa4ec36c29a6063ccdf89c48a74bfd/packages/material-ui/src/Icon/Icon.js#L12
*/
