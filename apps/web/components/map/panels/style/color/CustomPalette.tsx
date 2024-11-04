// Copyright (c) 2023 Uber Technologies, Inc.
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
import type { DragEndEvent } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { Box, IconButton, Stack, TextField, useTheme } from "@mui/material";
import React, { useMemo, useState } from "react";
import { v4 } from "uuid";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { isValidHex } from "@/lib/utils/helpers";
import type { ColorRange } from "@/lib/validations/layer";

import type { ColorItem } from "@/types/map/color";

import ColorPalette from "@/components/map/panels/style/color/ColorPalette";
import DropdownFooter from "@/components/map/panels/style/other/DropdownFooter";
import { SingleColorPopper } from "@/components/map/panels/style/other/SingleColorPopper";
import { SortableItem } from "@/components/map/panels/style/other/SortableItem";
import SortableWrapper from "@/components/map/panels/style/other/SortableWrapper";

type CustomPaletteProps = {
  customPalette: ColorRange;
  onApply: (palette: ColorRange) => void;
  onCancel: () => void;
};

const CustomPalette = ({ customPalette, onApply, onCancel }: CustomPaletteProps) => {
  const theme = useTheme();

  const [colors, setColors] = useState(
    customPalette.colors.map((color) => {
      return {
        id: v4(),
        color: color,
      };
    }) || []
  );

  const areColorsValid = useMemo(() => {
    let isValid = true;
    colors.forEach((color) => {
      if (!isValidHex(color.color)) {
        isValid = false;
      }
    });
    return isValid;
  }, [colors]);

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    const oldIndex = colors.findIndex((color) => color.id === active.id);
    const newIndex = colors.findIndex((color) => color.id === over?.id);
    const newOrderArray = arrayMove(colors, oldIndex, newIndex);
    setColors(newOrderArray);
  }

  function deleteColor(item: ColorItem) {
    if (colors.length === 2) {
      return;
    }
    const index = colors.findIndex((color) => color.id === item.id);
    if (index !== -1) {
      const newColors = colors.toSpliced(index, 1);
      setColors(newColors);
    }
  }

  function duplicateColor(item: ColorItem) {
    const index = colors.findIndex((color) => color.id === item.id);
    if (index !== -1) {
      const newColors = colors.toSpliced(index + 1, 0, {
        id: v4(),
        color: item.color,
      });
      setColors(newColors);
    }
  }

  function _onCancel() {
    onCancel();
  }

  function _onApply() {
    const newColorRange = {
      ...customPalette,
      type: "custom",
      colors: colors.map((color) => color.color),
    };
    onApply(newColorRange);
  }

  function onInputHexChange(item: ColorItem) {
    const index = colors.findIndex((color) => color.id === item.id);
    if (index !== -1) {
      const newColors = colors.toSpliced(index, 1, {
        ...item,
      });
      setColors(newColors);
    }
  }

  const [editingItem, setEditingItem] = React.useState<ColorItem | null>(null);
  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);

  const handleColorPicker = (event: React.MouseEvent<HTMLDivElement, MouseEvent>, item: ColorItem) => {
    setEditingItem(item);
    setAnchorEl(event.currentTarget);
  };

  return (
    <>
      <SingleColorPopper editingItem={editingItem} anchorEl={anchorEl} onInputHexChange={onInputHexChange} />

      <Box sx={{ px: 2 }}>
        <ColorPalette colors={colors.map((color) => color.color)} />
      </Box>
      <Box onClick={() => setEditingItem(null)} sx={{ maxHeight: "240px", overflowY: "auto" }}>
        <SortableWrapper handleDragEnd={handleDragEnd} items={colors}>
          {colors?.map((item) => (
            <SortableItem
              active={item.id === editingItem?.id}
              key={item.id}
              item={item}
              label={item.color}
              picker={
                <>
                  <Box
                    onClick={(e) => {
                      e.stopPropagation();
                      handleColorPicker(e, item);
                    }}
                    sx={{
                      height: "20px",
                      width: "32px",
                      borderRadius: "4px",
                      backgroundColor: item.color,
                      "&:hover": {
                        cursor: "pointer",
                      },
                    }}
                  />
                </>
              }
              actions={
                <Stack direction="row">
                  <IconButton size="small" onClick={() => duplicateColor(item)}>
                    <Icon
                      iconName={ICON_NAME.PLUS}
                      style={{
                        fontSize: 12,
                      }}
                      htmlColor="inherit"
                    />
                  </IconButton>
                  <IconButton size="small" onClick={() => deleteColor(item)}>
                    <Icon
                      iconName={ICON_NAME.TRASH}
                      style={{
                        fontSize: 12,
                      }}
                      htmlColor="inherit"
                    />
                  </IconButton>
                </Stack>
              }>
              <TextField
                InputProps={{ sx: { height: "32px", ml: 0, mr: 2 } }}
                sx={{
                  "& .MuiOutlinedInput-input": {
                    padding: `0 ${theme.spacing(2)}`,
                  },
                }}
                onChange={(e) => {
                  onInputHexChange({
                    ...item,
                    color: e.target.value.toUpperCase(),
                  });
                }}
                variant="outlined"
                value={item.color}
              />
            </SortableItem>
          ))}
        </SortableWrapper>
      </Box>
      <DropdownFooter isValid={areColorsValid} onCancel={_onCancel} onApply={_onApply} />
    </>
  );
};

export default CustomPalette;
