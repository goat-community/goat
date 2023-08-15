// Copyright (c) 2020 GitHub user u/garronej

export type { PaletteBase, ColorUseCasesBase, CreateColorUseCase } from "./color";

export { defaultPalette, createDefaultColorUseCases, changeColorOpacity } from "./color";

export type { TypographyDesc, ComputedTypography, GetTypographyDesc } from "./typography";
export { defaultGetTypographyDesc } from "./typography";

export * from "./breakpoints";
export { breakpointsValues } from "./breakpoints";

export type { SpacingConfig, Spacing } from "./spacing";
export { defaultSpacingConfig } from "./spacing";

export type { IconSizeName, GetIconSizeInPx } from "./icon";
export { defaultGetIconSizeInPx } from "./icon";

export type { Theme, ThemeProviderProps } from "./ThemeProvider";
export { createThemeProvider, useDomRect, ViewPortOutOfRangeError } from "./ThemeProvider";

export { pxToNumber } from "../tools/pxToNumber";
