// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/no-explicit-any */

export const iconSizeNames = ["extra small", "small", "default", "medium", "large", "extra large"] as const;

export type IconSizeName = (typeof iconSizeNames)[number];

export type GetIconSizeInPx = (params: { sizeName: IconSizeName; rootFontSizePx: number }) => number;

export const defaultGetIconSizeInPx: GetIconSizeInPx = ({ sizeName, rootFontSizePx }) =>
  rootFontSizePx *
  (() => {
    switch (sizeName) {
      case "extra small":
        return 1;
      case "small":
        return 1;

      case "default":
        return 1.25;
      case "medium":
        return 1.25;

      case "large":
        return 1.5;
      case "extra large":
        return 2;
    }
  })();

export function getIconSizesInPxByName(params: {
  getIconSizeInPx: GetIconSizeInPx;
  rootFontSizePx: number;
}): Record<IconSizeName, number> {
  const { getIconSizeInPx, rootFontSizePx } = params;

  const out: ReturnType<typeof getIconSizesInPxByName> = {} as any;

  iconSizeNames.forEach(
    (sizeName) =>
      (out[sizeName] = getIconSizeInPx({
        rootFontSizePx,
        sizeName,
      }))
  );

  return out;
}
