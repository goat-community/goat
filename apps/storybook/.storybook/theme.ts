import { create } from "@storybook/theming";

export const darkTheme = create({
  base: "dark",
  appBg: "#18202B",
  appContentBg: "#18202B",
  barBg: "#18202B",
  colorSecondary: "#2BB381",
  textColor: "#ffffff",
  textInverseColor: "#18202B",
  brandImage: "https://plan4better.de/images/logo-light.png",
  brandTitle: "Plan4Better UI",
  brandUrl: "https://plan4better.de",
  fontBase: '"Work Sans","Open Sans", sans-serif',
  fontCode: "monospace",
});

export const lightTheme = create({
  base: "light",
  appBg: "#F4F5FA",
  appContentBg: "#F4F5FA",
  barBg: "#F4F5FA",
  colorSecondary: "#2BB381",
  textColor: "#283648",
  textInverseColor: "#F4F5FA",
  brandImage: "https://plan4better.de/images/logo.png",
  brandTitle: "Plan4Better UI",
  brandUrl: "https://plan4better.de",
  fontBase: '"Work Sans","Open Sans", sans-serif',
  fontCode: "monospace",
});
