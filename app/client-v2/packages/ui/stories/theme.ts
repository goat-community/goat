import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import type { Param0 } from "tsafe";

import "../assets/fonts/mulish/font.css";
import { createButton } from "../components/Button";
import { createIcon } from "../components/Icon";
import { createIconButton } from "../components/IconButton";
import { createText } from "../components/Text";
import { createThemeProvider, defaultGetTypographyDesc } from "../lib";

export const { ThemeProvider, StoryProvider, useTheme } = createThemeProvider({
  isReactStrictModeEnabled: false,
  getTypographyDesc: ({ windowInnerWidth, browserFontSizeFactor, windowInnerHeight }) => ({
    ...defaultGetTypographyDesc({
      windowInnerWidth,
      browserFontSizeFactor,
      windowInnerHeight,
    }),
    fontFamily: '"Mulish", sans-serif',
  }),
});

export const { Icon } = createIcon({
  help: HelpIcon,
  home: HomeIcon,
});

export type IconId = Param0<typeof Icon>["iconId"];

export const { IconButton } = createIconButton({ Icon });

export const { Button } = createButton({ Icon });

export const { Text } = createText({ useTheme });
