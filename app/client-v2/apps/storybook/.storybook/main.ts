import type { StorybookConfig } from "@storybook/nextjs";

const config: StorybookConfig = {
  stories: [
    "../../../packages/keycloak-theme/src/**/*.mdx",
    "../../../packages/keycloak-theme/src/**/*.stories.@(js|jsx|ts|tsx)",
    // "../../../packages/ui/stories/*.mdx",
    // "../../../packages/ui/stories/*.stories.@(js|jsx|ts|tsx)",
  ],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "storybook-dark-mode",
  ],
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  docs: {
    autodocs: "tag",
  },
  staticDirs: ["../public", "../../../packages/keycloak-theme/public"],
};
export default config;
