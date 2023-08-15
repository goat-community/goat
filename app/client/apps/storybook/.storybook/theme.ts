import { create } from "@storybook/theming";

export const lightTheme = create({
  base: "dark",
  appBg: "#283648",
  appContentBg: "#283648",
  barBg: "#283648",
  colorSecondary: "#2BB381",
  textColor: "#ffffff",
  brandImage: "https://plan4better.de/images/logo-light.png",
  brandTitle: "Plan4Better UI",
  brandUrl: "https://plan4better.de",
  fontBase: '"Work Sans","Open Sans", sans-serif',
  fontCode: "monospace",
});

export const darkTheme = create({
  base: "light",
  appBg: "#f1f0eb",
  appContentBg: "#f1f0eb",
  barBg: "#f1f0eb",
  colorSecondary: "#2BB381",
  textColor: "#283648",
  textInverseColor: "#f1f0eb",
  brandImage: "https://plan4better.de/images/logo.png",
  brandTitle: "Plan4Better UI",
  brandUrl: "https://plan4better.de",
  fontBase: '"Work Sans","Open Sans", sans-serif',
  fontCode: "monospace",
});
