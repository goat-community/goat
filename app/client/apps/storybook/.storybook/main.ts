import type { StorybookConfig } from "@storybook/nextjs";

const config: StorybookConfig = {
  core: {
    disableTelemetry: true,
  },
  stories: [
    "../../../packages/keycloak-theme/src/stories/*.mdx",
    "../../../packages/keycloak-theme/src/stories/*.stories.@(js|jsx|ts|tsx)",
    "../../../packages/ui/stories/**/*.mdx",
    "../../../packages/ui/stories/**/*.stories.@(js|jsx|ts|tsx)",
  ],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@storybook/addon-a11y",
    "storybook-dark-mode",
    "storybook-addon-designs",
  ],
  docs: {
    autodocs: "tag",
  },
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  staticDirs: ["../public", "../../../packages/keycloak-theme/public"],
};
export default config;
