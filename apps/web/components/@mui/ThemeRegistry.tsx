"use client";

import type { PaletteMode } from "@mui/material";
import React from "react";

import ThemeProvider from "@p4b/ui/theme/ThemeProvider";

import { useTranslation } from "@/i18n/client";

import NextAppDirEmotionCacheProvider from "./EmotionCache";

export const ColorModeContext = React.createContext({
  changeColorMode: (_mode: PaletteMode) => {},
});
export default function ThemeRegistry({
  children,
  theme,
}: {
  children: React.ReactNode;
  theme?: PaletteMode;
}) {
  const [mode, setMode] = React.useState<PaletteMode>(theme || "light");
  const { i18n } = useTranslation("common");
  const colorMode = React.useMemo(
    () => ({
      changeColorMode: (mode: PaletteMode) => {
        setMode(mode);
      },
    }),
    []
  );
  return (
    <>
      <ColorModeContext.Provider value={colorMode}>
        <NextAppDirEmotionCacheProvider options={{ key: "mui" }}>
          <ThemeProvider
            settings={{
              mode,
              locale: i18n?.language || "en",
            }}>
            {children}
          </ThemeProvider>
        </NextAppDirEmotionCacheProvider>
      </ColorModeContext.Provider>
    </>
  );
}
