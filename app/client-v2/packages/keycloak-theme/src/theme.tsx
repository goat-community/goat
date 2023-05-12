import CloseSharp from "@mui/icons-material/CloseSharp";

import { createButton } from "@p4b/ui/components/Button";
import { createIcon } from "@p4b/ui/components/Icon";
import { createIconButton } from "@p4b/ui/components/IconButton";
import { createText } from "@p4b/ui/components/Text";
import {
  createThemeProvider,
  defaultGetTypographyDesc,
  defaultPalette,
  createDefaultColorUseCases,
} from "@p4b/ui/lib";
import { createMakeAndWithStyles } from "@p4b/ui/lib/tss";

export const { ThemeProvider, useTheme } = createThemeProvider({
  getTypographyDesc: ({ windowInnerWidth, browserFontSizeFactor, windowInnerHeight }) => {
    const typographyDesc = defaultGetTypographyDesc({
      windowInnerWidth,
      browserFontSizeFactor,
      windowInnerHeight,
    });

    return {
      fontFamily: '"Work Sans", sans-serif',
      rootFontSizePx: typographyDesc.rootFontSizePx,
      variants: {
        ...typographyDesc.variants,
        "display heading": {
          ...typographyDesc.variants["display heading"],
          fontFamily: "Marianne, sans-serif",
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
export const { Button } = createButton({ Icon });
export const { IconButton } = createIconButton({ Icon });

export const logoContainerWidthInPercent = 4;
