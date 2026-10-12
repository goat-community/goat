import type { StorybookConfig } from "@storybook/nextjs";
import path from "path";

// Images the shared UI imports (e.g. the sign-in artwork). @storybook/nextjs
// routes image imports through its next/image loader, which needs sharp, and
// sharp has no prebuilt binary in the Alpine build image; served as plain
// files they need nothing.
const uiAssets = path.resolve(__dirname, "../../../packages/js/ui/assets");

const config: StorybookConfig = {
  core: {
    disableTelemetry: true,
  },
  stories: [
    "../../../packages/js/keycloak-theme/src/stories/*.mdx",
    "../../../packages/js/keycloak-theme/src/stories/*.stories.@(js|jsx|ts|tsx)",
    "../../../packages/js/ui/stories/**/*.mdx",
    "../../../packages/js/ui/stories/**/*.stories.@(js|jsx|ts|tsx)",
  ],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@storybook/addon-a11y",
    "storybook-dark-mode",
    "@storybook/addon-designs",
  ],
  docs: {
    autodocs: "tag",
  },
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  staticDirs: ["../public", "../../../packages/js/keycloak-theme/public"],
  webpackFinal: async (webpackConfig) => {
    webpackConfig.module ??= {};
    const rules = (webpackConfig.module.rules ??= []);
    for (const rule of rules) {
      const r = rule as { test?: unknown; exclude?: unknown } | null;
      if (r && r.test instanceof RegExp && r.test.test("image.png")) {
        r.exclude = [...(r.exclude ? [r.exclude].flat() : []), uiAssets];
      }
    }
    rules.push({ test: /\.(png|jpe?g|webp|gif)$/i, include: uiAssets, type: "asset/resource" });
    return webpackConfig;
  },
};
export default config;
