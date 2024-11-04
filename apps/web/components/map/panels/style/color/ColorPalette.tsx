// Copyright (c) 2023 Uber Technologies, Inc; Plan4Better GmbH
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
import { styled } from "@mui/material/styles";
import React from "react";

import type { HexColor, RGBColor } from "@/types/map/color";

type ColorPaletteProps = {
  colors: RGBColor | HexColor[];
  height?: number;
  isSelected?: boolean;
  isReversed?: boolean;
};

const PaletteWrapper = styled("div")({
  borderRadius: "2px",
  display: "flex",
  flexDirection: "row",
  flexGrow: 1,
  justifyContent: "space-between",
  overflow: "hidden",
  "&.color-range-palette__inner": {},
});

interface PaletteContainerProps {
  isSelected?: boolean;
}

const PaletteContainer = styled("div")<PaletteContainerProps>(({ theme, isSelected }) => ({
  display: "flex",
  flexGrow: 1,
  borderWidth: "2px",
  borderStyle: "solid",
  borderColor: isSelected ? theme.palette.primary.main : "transparent",
  padding: theme.spacing(1),
  borderRadius: theme.spacing(1),
}));

const StyledColorBlock = styled("div")({
  flexGrow: 1,
  "&.color-range-palette__block": {},
});
const ColorPalette: React.FC<ColorPaletteProps> = ({
  colors = [],
  height = 10,
  isSelected = false,
  isReversed = false,
}) => (
  <PaletteContainer isSelected={isSelected}>
    <PaletteWrapper style={{ height, transform: `scale(${isReversed ? -1 : 1}, 1)` }}>
      {colors.map((color: number | string, index: number) => (
        <StyledColorBlock key={`${color}-${index}`} style={{ backgroundColor: String(color) }} />
      ))}
    </PaletteWrapper>
  </PaletteContainer>
);

export default ColorPalette;
