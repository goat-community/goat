import CloseSharp from "@mui/icons-material/CloseSharp";

import "@p4b/ui/assets/fonts/mulish/font.css";
import { createButton } from "@p4b/ui/components/Button";
import { createText, createIconButton, createIcon } from "@p4b/ui/components/DataDisplay";
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
      rootFontSizePx: typographyDesc.rootFontSizePx,
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

export const { Icon } = createIcon({
  close: CloseSharp,
});

export const { makeStyles, useStyles } = createMakeAndWithStyles({ useTheme });
export const { Text } = createText({ useTheme });
export const { Button } = createButton({Icon});
export const { IconButton } = createIconButton({ Icon });

export const logoContainerWidthInPercent = 4;
