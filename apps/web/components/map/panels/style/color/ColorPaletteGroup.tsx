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
import { Box } from "@mui/material";

import { reverseColorRange } from "@/lib/utils/helpers";
import type { ColorRange } from "@/lib/validations/layer";

import ColorPalette from "@/components/map/panels/style/color/ColorPalette";

type ColorPaletteGroupProps = {
  reversed?: boolean;
  selected: ColorRange;
  colorRanges: ColorRange[];
  onSelect: (p: ColorRange) => void;
};

const ColorPaletteGroup = (props: ColorPaletteGroupProps) => {
  const { reversed, selected, colorRanges, onSelect } = props;

  return (
    <Box
      sx={{
        px: 3,
        maxHeight: "300px",
        overflowY: "auto",
      }}>
      {colorRanges.map((colorRange, i) => (
        <Box
          sx={{
            m: 0,
            p: 0,
            "&:hover": {
              cursor: "pointer",
            },
          }}
          key={`${colorRange.name}-${i}`}
          onClick={() =>
            onSelect(reversed ? (reverseColorRange(true, colorRange) as ColorRange) : colorRange)
          }>
          <ColorPalette
            colors={colorRange.colors}
            isReversed={reversed}
            isSelected={colorRange.name === selected.name && reversed === Boolean(selected.reversed)}
          />
        </Box>
      ))}
    </Box>
  );
};

export default ColorPaletteGroup;
