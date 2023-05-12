// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/no-explicit-any */
import { breakpointsValues } from "./breakpoints";

export const iconSizeNames = ["extra small", "small", "default", "medium", "large"] as const;

export type IconSizeName = (typeof iconSizeNames)[number];

export type GetIconSizeInPx = (params: {
  sizeName: IconSizeName;
  windowInnerWidth: number;
  rootFontSizePx: number;
}) => number;

export const defaultGetIconSizeInPx: GetIconSizeInPx = ({ sizeName, windowInnerWidth, rootFontSizePx }) =>
  rootFontSizePx *
  (() => {
    switch (sizeName) {
      case "extra small":
        return 1;
      case "small":
        if (windowInnerWidth >= breakpointsValues.lg) {
          return 1.25;
        }

        return 1;

      case "default":
        if (windowInnerWidth >= breakpointsValues.lg) {
          return 1.5;
        }

        return 1.25;
      case "medium":
        if (windowInnerWidth >= breakpointsValues.lg) {
          return 2;
        }

        return 1.25;

      case "large":
        if (windowInnerWidth >= breakpointsValues.xl) {
          return 2.5;
        }

        if (windowInnerWidth >= breakpointsValues.lg) {
          return 2;
        }

        return 1.5;
    }
  })();

export function getIconSizesInPxByName(params: {
  getIconSizeInPx: GetIconSizeInPx;
  windowInnerWidth: number;
  rootFontSizePx: number;
}): Record<IconSizeName, number> {
  const { getIconSizeInPx, windowInnerWidth, rootFontSizePx } = params;

  const out: ReturnType<typeof getIconSizesInPxByName> = {} as any;

  iconSizeNames.forEach(
    (sizeName) =>
      (out[sizeName] = getIconSizeInPx({
        windowInnerWidth,
        rootFontSizePx,
        sizeName,
      }))
  );

  return out;
}
