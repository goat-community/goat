import { Box, Fade, Popper } from "@mui/material";

import { rgbToHex } from "@/lib/utils/helpers";

import type { ColorItem } from "@/types/map/color";

import SingleColorSelector from "@/components/map/panels/style/color/SingleColorSelector";

export function SingleColorPopper(props: {
  editingItem: ColorItem | null;
  anchorEl: HTMLElement | null;
  onInputHexChange: (item: ColorItem) => void;
}) {
  return (
    <Popper
      open={props.editingItem !== null}
      anchorEl={props.anchorEl}
      transition
      sx={{ zIndex: 2000, maxWidth: "240px" }}
      placement="left"
      modifiers={[
        {
          name: "offset",
          options: {
            offset: [0, 75],
          },
        },
      ]}>
      {({ TransitionProps }) => (
        <Fade {...TransitionProps}>
          <Box sx={{ py: 3, bgcolor: "background.paper", borderRadius: 1 }}>
            {props.editingItem && (
              <SingleColorSelector
                selectedColor={props.editingItem?.color || "#000000"}
                onSelectColor={(color) => {
                  if (props.editingItem)
                    props.onInputHexChange({
                      ...props.editingItem,
                      color: rgbToHex(color),
                    });
                }}
              />
            )}
          </Box>
        </Fade>
      )}
    </Popper>
  );
}
