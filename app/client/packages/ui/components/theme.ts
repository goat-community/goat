import { createButton } from "../components/Button";
import { createThemeProvider, defaultGetTypographyDesc } from "../lib";
import { createText } from "./Text";

export const { ThemeProvider, StoryProvider, useTheme } = createThemeProvider({
  isReactStrictModeEnabled: false,
  getTypographyDesc: () => ({
    ...defaultGetTypographyDesc(),
    fontFamily: "'Mulish', sans-serif",
    rootFontSizePx: 16,
  }),
});

export const { Button } = createButton();
export const { Text } = createText({ useTheme });
