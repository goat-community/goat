// Copyright (c) 2020 GitHub user u/garronej
import type { PaletteOptions as MuiPaletteOptions } from "@mui/material/styles/createPalette";
import type { Param0 } from "tsafe";

import { changeColorOpacity } from "../tools/changeColorOpacity";

export * from "../tools/changeColorOpacity";

export type PaletteBase = typeof defaultPalette;
export type ColorUseCasesBase = ReturnType<typeof createDefaultColorUseCases>;

export type CreateColorUseCase<
  Palette extends PaletteBase,
  ColorUseCases extends ColorUseCasesBase,
> = (params: { isDarkModeEnabled: boolean; palette: Palette }) => ColorUseCases;

export const defaultPalette = {
  focus: {
    main: "#2BB381",
    light: "#80D1B3",
    light2: "#60D3A2",
    dark: "#1A6B4D",
    darkVariant2: "#2bb3810a",
    darkVariant3: "#2BB3814D",
  },
  dark: {
    main: "#283648",
    light: "#647183",
    greyVariant1: "#18202B",
    greyVariant2: "#1E2F41",
    greyVariant3: "#425066",
    greyVariant4: "#6A7C91",
  },
  light: {
    main: "#FAFAFA",
    light: "#ffffff",
    greyVariant1: "#f2f2f3",
    greyVariant2: "#C9C9C9",
    greyVariant3: "#9E9E9E",
    greyVariant4: "#747474",
  },
  redError: {
    main: "#CC0B0B",
    light: "#FEECEB",
  },
  greenSuccess: {
    main: "#2E7D32",
    light: "#EEFAEE",
  },
  orangeWarning: {
    main: "#FF8800",
    light: "#FFF5E5",
  },
  blueInfo: {
    main: "#2196F3",
    light: "#E9F5FE",
  },
};

/* eslint-disable */
export function createDefaultColorUseCases(params: Param0<CreateColorUseCase<PaletteBase, any>>) {
  const { palette } = params;
  // const { isDarkModeEnabled } = params;
  const isDarkModeEnabled = false;
  return {
    typography: {
      textPrimary: palette[isDarkModeEnabled ? "light" : "dark"].main,
      textSecondary: isDarkModeEnabled ? palette.light.greyVariant2 : palette.light.greyVariant4,
      textTertiary: palette[isDarkModeEnabled ? "dark" : "light"].greyVariant2,
      textDisabled: palette[isDarkModeEnabled ? "dark" : "light"].greyVariant2,
      textFocus: palette.focus[isDarkModeEnabled ? "light" : "main"],
    },
    buttons: {
      actionHoverPrimary: palette.focus[isDarkModeEnabled ? "light" : "main"],
      actionHoverSecondary: isDarkModeEnabled ? palette.light.light : palette.dark.main,
      actionHoverTernary: palette.light.main,
      actionSelected: isDarkModeEnabled ? palette.dark.light : palette.light.greyVariant1,
      actionActive: palette.focus[isDarkModeEnabled ? "light" : "main"],
      actionDisabled: palette[isDarkModeEnabled ? "dark" : "light"].greyVariant3,
      actionDisabledBackground: palette[isDarkModeEnabled ? "dark" : "light"].greyVariant1,
    },
    surfaces: {
      background: palette[isDarkModeEnabled ? "dark" : "light"].main,
      surface1: palette[isDarkModeEnabled ? "dark" : "light"].light,
      surface2: palette[isDarkModeEnabled ? "dark" : "light"].greyVariant1,
    },
    alertSeverity: {
      error: {
        main: palette.redError.main,
        background: isDarkModeEnabled
          ? changeColorOpacity({
              color: palette.redError.main,
              opacity: 0.2,
            })
          : palette.redError.light,
      },
      success: {
        main: palette.greenSuccess.main,
        background: isDarkModeEnabled
          ? changeColorOpacity({
              color: palette.greenSuccess.main,
              opacity: 0.2,
            })
          : palette.greenSuccess.light,
      },
      warning: {
        main: palette.orangeWarning.main,
        background: isDarkModeEnabled
          ? changeColorOpacity({
              color: palette.orangeWarning.main,
              opacity: 0.2,
            })
          : palette.orangeWarning.light,
      },
      info: {
        main: palette.blueInfo.main,
        background: isDarkModeEnabled
          ? changeColorOpacity({
              color: palette.blueInfo.main,
              opacity: 0.2,
            })
          : palette.blueInfo.light,
      },
    },
  };
}

export function createMuiPaletteOptions(params: {
  isDarkModeEnabled: boolean;
  palette: PaletteBase;
  useCases: ColorUseCasesBase;
}): MuiPaletteOptions {
  const { isDarkModeEnabled, palette, useCases } = params;

  return {
    mode: isDarkModeEnabled ? "dark" : "light",
    primary: {
      main: palette.focus[isDarkModeEnabled ? "light" : "main"],
      light: palette.focus.light2,
      dark: palette.focus.dark,
    },
    secondary: {
      main: useCases.typography.textPrimary,
      light: useCases.typography.textSecondary,
    },
    error: {
      light: useCases.alertSeverity.error.background,
      main: useCases.alertSeverity.error.main,
      contrastText: useCases.typography.textPrimary,
    },
    success: {
      light: useCases.alertSeverity.success.background,
      main: useCases.alertSeverity.success.main,
      contrastText: useCases.typography.textPrimary,
    },
    info: {
      light: useCases.alertSeverity.info.background,
      main: useCases.alertSeverity.info.main,
      contrastText: useCases.typography.textPrimary,
    },
    warning: {
      light: useCases.alertSeverity.warning.background,
      main: useCases.alertSeverity.warning.main,
      contrastText: useCases.typography.textPrimary,
    },
    text: {
      primary: useCases.typography.textPrimary,
      secondary: useCases.typography.textSecondary,
      disabled: useCases.typography.textDisabled,
    },
    divider: useCases.buttons.actionDisabledBackground,
    background: {
      paper: useCases.surfaces.surface1,
      default: useCases.surfaces.background,
    },
    action: {
      active: useCases.buttons.actionActive,
      hover: palette.focus.light,
      selected: useCases.buttons.actionSelected,
      disabled: useCases.buttons.actionDisabled,
      disabledBackground: useCases.buttons.actionDisabledBackground,
      focus: useCases.typography.textFocus,
    },
  } as const;
}
