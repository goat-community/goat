// Copyright (c) 2020 GitHub user u/garronej
export function pxToNumber(str: `${number}px`): number {
  return Number.parseFloat(str.split("px")[0]);
}
