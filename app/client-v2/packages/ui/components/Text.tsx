// Copyright (c) 2020 GitHub user u/garronej
import { createElement, forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";
import { createMakeStyles } from "tss-react";

import type { Theme } from "../lib/ThemeProvider";
import type { PaletteBase, ColorUseCasesBase } from "../lib/color";
import type { TypographyDesc } from "../lib/typography";

export function createText<TypographyVariantNameCustom extends string = never>(params: {
  useTheme(): Theme<PaletteBase, ColorUseCasesBase, TypographyVariantNameCustom>;
}) {
  const { useTheme } = params;

  const { makeStyles } = createMakeStyles({ useTheme });

  type TextProps = {
    className?: string | null;
    typo: TypographyVariantNameCustom | TypographyDesc.VariantNameBase;
    color?: "primary" | "secondary" | "disabled" | "focus" | undefined;
    children: React.ReactNode;
    htmlComponent?: TypographyDesc.HtmlComponent;
    componentProps?: JSX.IntrinsicElements[TypographyDesc.HtmlComponent];

    fixedSize_enabled?: boolean;
    fixedSize_content?: string;
    fixedSize_fontWeight?: number;
  };

  const Text = memo(
    forwardRef<any, TextProps>((props, ref) => {
      const {
        className,
        children,
        typo,
        color = "primary",
        htmlComponent,
        componentProps = {},
        fixedSize_enabled = false,
        fixedSize_content,
        fixedSize_fontWeight,
        //For the forwarding, rest should be empty (typewise)
        ...rest
      } = props;

      //For the forwarding, rest should be empty (typewise),
      // eslint-disable-next-line @typescript-eslint/ban-types
      assert<Equals<typeof rest, {}>>();

      const theme = useTheme();

      const { classes, cx } = useStyles({
        typo,
        color,
        fixedSize_enabled,
        fixedSize_content,
        fixedSize_fontWeight,
        children: typeof children === "string" ? (children as string) : undefined,
      });

      return createElement(
        htmlComponent ?? theme.typography.variants[typo].htmlComponent,
        {
          className: cx(classes.root, className),
          ref,
          ...componentProps,
          ...rest,
        },
        children
      );
    })
  );

  const useStyles = makeStyles<
    {
      color: NonNullable<TextProps["color"]>;
      children: string | undefined;
    } & Pick<TextProps, "typo" | "fixedSize_enabled" | "fixedSize_content" | "fixedSize_fontWeight">
  >({ name: "Text" })(
    (theme, { typo, color, fixedSize_enabled, fixedSize_fontWeight, fixedSize_content, children }) => ({
      root: {
        ...theme.typography.variants[typo].style,
        color:
          theme.colors.useCases.typography[
            (() => {
              switch (color) {
                case "primary":
                  return "textPrimary";
                case "secondary":
                  return "textSecondary";
                case "disabled":
                  return "textDisabled";
                case "focus":
                  return "textFocus";
              }
            })()
          ],
        padding: 0,
        margin: 0,
        ...(!fixedSize_enabled
          ? {}
          : {
              display: "inline-flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "space-between",
              "&::after": {
                content: fixedSize_content
                  ? `"${fixedSize_content}"`
                  : (assert(children !== undefined), `"${children}_"`),
                height: 0,
                visibility: "hidden",
                overflow: "hidden",
                userSelect: "none",
                pointerEvents: "none",
                fontWeight: `${fixedSize_fontWeight}`,
                "@media speech": {
                  display: "none",
                },
              },
            }),
      },
    })
  );

  return { Text };
}
