// Copyright (c) 2020 GitHub user u/garronej
export function getIsDarkModeEnabledOsDefault() {
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
}
