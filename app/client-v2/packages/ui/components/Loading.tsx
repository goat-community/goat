"use client";

import { DotPulse, Ring } from "@uiball/loaders";

import { useTheme } from "./theme";

export type LoadingProps = {
  loadingType?: "ring" | "dotpulse";
  size?: number;
  color?: string;
  speed?: number;
};

export const defaultProps: LoadingProps = {
  loadingType: "dotpulse",
  size: 60,
  color: "black",
  speed: 1.3,
};

export function Loading(props: LoadingProps = defaultProps) {
  const theme = useTheme();
  const color = theme.colors.palette.focus.main;
  props = { ...defaultProps, ...props, color };
  return props.loadingType === "ring" ? <Ring {...props} /> : <DotPulse {...props} />;
}
