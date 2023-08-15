import "@p4b/ui/assets/fonts/mulish/font.css";
import { createText } from "@p4b/ui/components/Text";
import {
  createThemeProvider,
  defaultGetTypographyDesc,
  defaultPalette,
  createDefaultColorUseCases,
} from "@p4b/ui/lib";
import { createMakeAndWithStyles } from "@p4b/ui/lib/tss";

export const { ThemeProvider, useTheme } = createThemeProvider({
  getTypographyDesc: () => {
    const typographyDesc = defaultGetTypographyDesc();

    return {
      fontFamily: '"Mulish", sans-serif',
      rootFontSizePx: 16,
      variants: {
        ...typographyDesc.variants,
        "display heading": {
          ...typographyDesc.variants["display heading"],
          fontFamily: "Mulish, sans-serif",
        },
      },
    };
  },
  palette: {
    ...defaultPalette,
  },
  createColorUseCases: ({ isDarkModeEnabled, palette }) => ({
    ...createDefaultColorUseCases({ isDarkModeEnabled, palette }),
  }),
});

export const { makeStyles, useStyles } = createMakeAndWithStyles({ useTheme });
export const { Text } = createText({ useTheme });
export const logoContainerWidthInPercent = 4;
