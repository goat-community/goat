import { useStyles } from "../../lib/ThemeProvider";
import { createText } from "./Text";

function useTheme() {
  const { theme } = useStyles();
  return theme;
}

export const { Text } = createText({ useTheme });
