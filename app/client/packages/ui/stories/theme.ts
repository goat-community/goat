import "../assets/fonts/mulish/font.css";
import { createThemeProvider, defaultGetTypographyDesc } from "../lib";
import { createText } from "../components/Text";

export const { ThemeProvider, StoryProvider, useTheme } = createThemeProvider({
  isReactStrictModeEnabled: false,
  getTypographyDesc: () => ({
    ...defaultGetTypographyDesc(),
    fontFamily: '"Mulish", sans-serif',
  }),
});

export const { Text } = createText({ useTheme });
