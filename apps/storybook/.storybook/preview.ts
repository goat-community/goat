import type { Preview } from "@storybook/react";
import React from "react";

import { DocsContainer } from "@storybook/addon-docs";
import { useDarkMode } from "storybook-dark-mode";
import { darkTheme, lightTheme } from "./theme";

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
    docs: {
      container: (props) => {
        const isDark = useDarkMode();
        const currentProps = { ...props };
        currentProps.theme = isDark ? darkTheme : lightTheme;
        return React.createElement(DocsContainer, currentProps);
      },
    },
    darkMode: {
      dark: darkTheme,
      light: lightTheme
    },
    viewport: {
      viewports: {
        "4k": {
          name: "4K",
          styles: {
            width: "3840px",
            height: "2160px",
          },
        },
        "1440p": {
          name: "1440p",
          styles: {
            width: "2560px",
            height: "1440px",
          },
        },
        fullHD: {
          name: "Full HD",
          styles: {
            width: "1920px",
            height: "1080px",
          },
        },
        hd: {
          name: "HD",
          styles: {
            width: "1366px",
            height: "768px",
          },
        },
        verySmallLandscape: {
          name: "Very small landscape",
          styles: {
            width: "599px",
            height: "337px",
          },
        },
      },
    },
    options: {
      storySort: {
        order: ["introduction", "foundations", "components", "pages"],
      },
    },
  },
};

export default preview;
