//Copyright (c) 2020 GitHub user u/garronej
import type { FC, ComponentClass } from "react";

// eslint-disable-next-line @typescript-eslint/ban-types
export type ReactComponent<Props extends Record<string, unknown> = {}> =
  | ((props: Props) => ReturnType<FC>)
  | ComponentClass<Props>;
