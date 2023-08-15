import type { FC, ReactNode } from "react";
import { createElement } from "react";

interface WrapProps {
  if?: boolean;
  with: (typeof createElement.arguments)[0];
  wrapperProps: (typeof createElement.arguments)[1];
  children: NonNullable<ReactNode>;
}

export const Wrap: FC<WrapProps> = ({
  if: condition = true,
  with: wrapper = "div",
  wrapperProps = {},
  children,
}) => (condition ? createElement(wrapper, wrapperProps, [children]) : <>children</>);
