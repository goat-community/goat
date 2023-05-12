// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable @typescript-eslint/no-explicit-any */

/* eslint-disable @typescript-eslint/no-namespace */
import type { Theme as MuiTheme } from "@mui/material";
import CssBaseline from "@mui/material/CssBaseline";
import ScopedCssBaseline from "@mui/material/ScopedCssBaseline";
import { ThemeProvider as MuiThemeProvider } from "@mui/material/styles";
import { createTheme as createMuiTheme, unstable_createMuiStrictModeTheme } from "@mui/material/styles";
import memoize from "memoizee";
import "minimal-polyfills/Object.fromEntries";
import { ViewPortAdapter, ViewPortOutOfRangeError } from "powerhooks/ViewPortAdapter";
import type { ViewPortAdapterProps } from "powerhooks/ViewPortAdapter";
import { useBrowserFontSizeFactor } from "powerhooks/useBrowserFontSizeFactor";
import { useGuaranteedMemo } from "powerhooks/useGuaranteedMemo";
import { useWindowInnerSize } from "powerhooks/useWindowInnerSize";
import { useContext, createContext, useEffect } from "react";
import type { ReactNode } from "react";
import React from "react";
import { capitalize } from "tsafe/capitalize";
import { id } from "tsafe/id";
import { createMakeAndWithStyles } from "tss-react";

import type { ReactComponent } from "../tools/ReactComponent";
import { createSplashScreen } from "./SplashScreen";
import type { SplashScreenProps } from "./SplashScreen";
import { breakpointsValues } from "./breakpoints";
import type { PaletteBase, ColorUseCasesBase, CreateColorUseCase } from "./color";
import { defaultPalette, createDefaultColorUseCases } from "./color";
import { createMuiPaletteOptions } from "./color";
import type { IconSizeName, GetIconSizeInPx } from "./icon";
import { defaultGetIconSizeInPx, getIconSizesInPxByName } from "./icon";
import { shadows } from "./shadows";
import { defaultSpacingConfig } from "./spacing";
import type { SpacingConfig, Spacing } from "./spacing";
import type { ComputedTypography, GetTypographyDesc } from "./typography";
import { defaultGetTypographyDesc, createMuiTypographyOptions, getComputedTypography } from "./typography";
import { useIsDarkModeEnabled, evtIsDarkModeEnabled } from "./useIsDarkModeEnabled";

export { useDomRect } from "powerhooks/useDomRect";
export { useWindowInnerSize, useBrowserFontSizeFactor };
export { ViewPortOutOfRangeError };

export type Theme<
  Palette extends PaletteBase = PaletteBase,
  ColorUseCases extends ColorUseCasesBase = ColorUseCasesBase,
  CustomTypographyVariantName extends string = never
> = {
  colors: {
    palette: Palette;
    useCases: ColorUseCases;
  };
  isDarkModeEnabled: boolean;
  typography: ComputedTypography<CustomTypographyVariantName>;
  shadows: typeof shadows;
  spacing: Spacing;
  muiTheme: MuiTheme;
  iconSizesInPxByName: Record<IconSizeName, number>;
  windowInnerWidth: number;
};

const themeBaseContext = createContext<Theme | undefined>(undefined);
const isDarkModeEnabledOverrideContext = createContext<boolean | undefined>(undefined);

/** Used internally, do not export globally */

export function useIsThemeProvided(): boolean {
  const theme = useContext(themeBaseContext);

  return theme !== undefined;
}

function useThemeBase() {
  const theme = useContext(themeBaseContext);

  if (theme === undefined) {
    throw new Error("Your app should be wrapped into ThemeProvider");
  }

  return theme;
}

export const { makeStyles, useStyles } = createMakeAndWithStyles({
  useTheme: useThemeBase,
});

export type ThemeProviderProps = {
  children: ReactNode;
  /** NOTE: Each time the callback's ref update the
   * the callback will be invoked again, it's best
   * a cont callback */
  getViewPortConfig?: ViewPortAdapterProps["getConfig"];
  splashScreen?: Omit<SplashScreenProps, "children">;
};

export declare namespace ThemeProviderProps {
  type WithChildren = {
    children: ReactNode;
  };

  export type WithZoom = {
    zoomProviderReferenceWidth?: number;

    /**
     * Message to display when portrait mode, example:
     *    This app isn't compatible with landscape mode yet,
     *    please enable the rotation sensor and flip your phone.
     */
    portraitModeUnsupportedMessage?: ReactNode;
  } & WithChildren;

  export type WithoutZoom = WithChildren;
}

export function createThemeProvider<
  Palette extends PaletteBase = PaletteBase,
  ColorUseCases extends ColorUseCasesBase = ColorUseCasesBase,
  CustomTypographyVariantName extends string = never
>(params: {
  isReactStrictModeEnabled?: boolean;
  getTypographyDesc?: GetTypographyDesc<CustomTypographyVariantName>;
  palette?: Palette;
  createColorUseCases?: CreateColorUseCase<Palette, ColorUseCases>;
  spacingConfig?: SpacingConfig;
  defaultIsDarkModeEnabled?: boolean;
  getIconSizeInPx?: GetIconSizeInPx;
  /** Default true */
}) {
  const {
    palette = defaultPalette as NonNullable<(typeof params)["palette"]>,
    createColorUseCases = createDefaultColorUseCases as unknown as NonNullable<
      (typeof params)["createColorUseCases"]
    >,
    getTypographyDesc = defaultGetTypographyDesc as NonNullable<(typeof params)["getTypographyDesc"]>,
    isReactStrictModeEnabled = false,
    spacingConfig = defaultSpacingConfig,
    defaultIsDarkModeEnabled,
    getIconSizeInPx = defaultGetIconSizeInPx,
  } = params;

  if (defaultIsDarkModeEnabled !== undefined) {
    evtIsDarkModeEnabled.state = defaultIsDarkModeEnabled;
  }

  const { useTheme } = (() => {
    const createTheme = memoize(
      (
        isDarkModeEnabled: boolean,
        windowInnerWidth: number,
        windowInnerHeight: number,
        browserFontSizeFactor: number
      ) => {
        const typographyDesc = getTypographyDesc({
          windowInnerWidth,
          windowInnerHeight,
          browserFontSizeFactor,
        });
        const useCases = createColorUseCases({
          palette,
          isDarkModeEnabled,
        });

        const spacing = (factorOrExplicitNumberOfPx: number | `${number}px`) =>
          spacingConfig({
            factorOrExplicitNumberOfPx,
            windowInnerWidth,
            rootFontSizePx: typographyDesc.rootFontSizePx,
          });

        return id<Theme<Palette, ColorUseCases, CustomTypographyVariantName>>({
          colors: { palette, useCases },
          typography: getComputedTypography({ typographyDesc }),
          isDarkModeEnabled,
          shadows,
          ...(() => {
            const muiTheme = (isReactStrictModeEnabled ? unstable_createMuiStrictModeTheme : createMuiTheme)({
              // https://material-ui.com/customization/palette/#using-a-color-object
              typography: createMuiTypographyOptions({
                typographyDesc,
              }),
              palette: createMuiPaletteOptions({
                isDarkModeEnabled,
                palette,
                useCases,
              }),
              spacing,
              breakpoints: {
                values: { xs: 0, ...breakpointsValues },
              },
              components: {
                MuiLink: {
                  defaultProps: {
                    underline: "hover",
                  },
                },
              },
            });

            return {
              spacing: (() => {
                const toFinalValue = (value: number | string) =>
                  typeof value === "number" ? `${spacing(value)}px` : value;

                const out = ((
                  valueOrObject: number | Record<"topBottom" | "rightLeft", number | string>
                ): string | number => {
                  if (typeof valueOrObject === "number") {
                    return spacing(valueOrObject);
                  }

                  const { rightLeft, topBottom } = valueOrObject;

                  return [topBottom, rightLeft, topBottom, rightLeft].map(toFinalValue).join(" ");
                }) as any as Spacing;

                const f = (params: {
                  axis: "vertical" | "horizontal";
                  kind: "padding" | "margin";
                  value: number | string;
                }): Record<string, string> => {
                  const { axis, kind, value } = params;

                  const finalValue = typeof value === "number" ? `${spacing(value)}px` : value;

                  return Object.fromEntries(
                    (() => {
                      switch (axis) {
                        case "horizontal":
                          return ["left", "right"];
                        case "vertical":
                          return ["top", "bottom"];
                      }
                    })().map((direction) => [`${kind}${capitalize(direction)}`, finalValue])
                  );
                };

                out.rightLeft = (kind: any, value: any) => f({ axis: "horizontal", kind, value });
                out.topBottom = (kind: any, value: any) => f({ axis: "vertical", kind, value });

                return out;
              })(),
              muiTheme,
            };
          })(),
          iconSizesInPxByName: getIconSizesInPxByName({
            getIconSizeInPx,
            windowInnerWidth,
            rootFontSizePx: typographyDesc.rootFontSizePx,
          }),
          windowInnerWidth,
        });
      },
      { max: 1 }
    );

    function useTheme() {
      const { isDarkModeEnabled } = useIsDarkModeEnabled();
      const { windowInnerWidth, windowInnerHeight } = useWindowInnerSize();
      const { browserFontSizeFactor } = useBrowserFontSizeFactor();

      const isDarkModeEnabledOverride = useContext(isDarkModeEnabledOverrideContext);

      return createTheme(
        isDarkModeEnabledOverride ?? isDarkModeEnabled,
        windowInnerWidth,
        windowInnerHeight,
        browserFontSizeFactor
      );
    }

    return { useTheme };
  })();

  const { SplashScreen } = createSplashScreen({ useTheme });

  const { ThemeProvider } = (() => {
    function ThemeProviderWithinViewPortAdapter(props: {
      splashScreen: ThemeProviderProps["splashScreen"];
      children: ReactNode;
    }) {
      const { splashScreen, children } = props;

      const theme = useTheme();

      {
        const backgroundColor = theme.colors.useCases.surfaces.background;

        useEffect(() => {
          document.querySelector("meta[name=theme-color]")?.remove();
          document.head.insertAdjacentHTML(
            "beforeend",
            `<meta name="theme-color" content="${backgroundColor}">`
          );
        }, [backgroundColor]);
      }

      const isStoryProvider = useContext(isDarkModeEnabledOverrideContext) !== undefined;

      // prettier-ignore
      const CssBaselineOrScopedCssBaseline = useGuaranteedMemo(
                (): ReactComponent<{ children: ReactNode }> =>
                    isStoryProvider
                        ? ({ children }) => (<ScopedCssBaseline>{children}</ScopedCssBaseline>)
                        : ({ children }) => (<><CssBaseline />{children}</>),
                [isStoryProvider],
            );

      // prettier-ignore
      const SplashScreenOrId = useGuaranteedMemo(
                (): ReactComponent<{ children: ReactNode }> =>
                    splashScreen === undefined ?
                        (({ children }) => <>{children}</>) :
                        (({ children }) => <SplashScreen {...splashScreen}>{children}</SplashScreen>),
                [splashScreen],
            );

      return (
        <themeBaseContext.Provider value={theme}>
          <MuiThemeProvider theme={theme.muiTheme}>
            <CssBaselineOrScopedCssBaseline>
              <SplashScreenOrId>{children}</SplashScreenOrId>
            </CssBaselineOrScopedCssBaseline>
          </MuiThemeProvider>
        </themeBaseContext.Provider>
      );
    }

    function ThemeProvider(props: ThemeProviderProps) {
      const { getViewPortConfig, children, splashScreen } = props;

      // prettier-ignore
      const ViewPortAdapterOrId = useGuaranteedMemo(
                (): ReactComponent<{ children: ReactNode; }> => getViewPortConfig === undefined ?
                    (({ children }) => <>{children}</>) :
                    (({ children }) => <ViewPortAdapter getConfig={getViewPortConfig}>{children}</ViewPortAdapter>),
                [getViewPortConfig]
            );

      return (
        <ViewPortAdapterOrId>
          <ThemeProviderWithinViewPortAdapter splashScreen={splashScreen}>
            {children}
          </ThemeProviderWithinViewPortAdapter>
        </ViewPortAdapterOrId>
      );
    }

    return { ThemeProvider };
  })();

  function StoryProvider(props: { dark?: boolean; children: ReactNode }) {
    const { dark = false, children } = props;

    useEffect(() => {
      evtIsDarkModeEnabled.state = dark;
    }, [dark]);

    return (
      <isDarkModeEnabledOverrideContext.Provider value={dark}>
        <ThemeProvider>{children}</ThemeProvider>
      </isDarkModeEnabledOverrideContext.Provider>
    );
  }

  const { makeStyles, useStyles, withStyles } = createMakeAndWithStyles({
    useTheme,
  });

  return {
    ThemeProvider,
    useTheme,
    StoryProvider,
    makeStyles,
    useStyles,
    withStyles,
  };
}
