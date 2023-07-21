// Copyright (c) 2020 GitHub user u/garronej
import { assert } from "tsafe/assert";

export interface Spacing {
  (value: number): number;
  (params: Record<"topBottom" | "rightLeft", number | string>): string;
  rightLeft<Kind extends "padding" | "margin">(
    kind: Kind,
    value: number | string
  ): Record<`${"left" | "right"}${Capitalize<Kind>}`, string>;
  topBottom<Kind extends "padding" | "margin">(
    kind: Kind,
    value: number | string
  ): Record<`${"top" | "bottom"}${Capitalize<Kind>}`, string>;
}

/** Return number of pixel */
export type SpacingConfig = (params: {
  /** Assert positive integer */
  factorOrExplicitNumberOfPx: number | `${number}px`;
  rootFontSizePx: number;
}) => number;

export const defaultSpacingConfig: SpacingConfig = ({ factorOrExplicitNumberOfPx, rootFontSizePx }) => {
  if (typeof factorOrExplicitNumberOfPx === "string") {
    const match = factorOrExplicitNumberOfPx.match(/^([+-]?([0-9]*[.])?[0-9]+)px$/);

    assert(match !== null, `${factorOrExplicitNumberOfPx} don't match \\d+px`);

    return Number.parseFloat(match[1]);
  }

  return (
    rootFontSizePx *
    (function callee(factor: number): number {
      assert(factor >= 0, "factor must be positive");

      if (!Number.isInteger(factor)) {
        return (callee(Math.floor(factor)) + callee(Math.floor(factor) + 1)) / 2;
      }

      if (factor === 0) {
        return 0;
      }

      if (factor > 6) {
        return (factor - 5) * callee(6);
      }

      switch (factor) {
        case 1:
          return 0.25;
        case 2:
          return 0.5;
        case 3:
          return 1;
        case 4:
          return 1.5;
        case 5:
          return 2;
        case 6:
          return 2.875;
      }

      assert(false);
    })(factorOrExplicitNumberOfPx)
  );
};
