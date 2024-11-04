import { Box, Fade, Popper } from "@mui/material";

import type { MarkerItem } from "@/types/map/marker";

import MarkerGallery from "@/components/map/panels/style/marker/MarkerGallery";

export function MarkerPopper(props: {
  editingItem: MarkerItem | null;
  anchorEl: HTMLElement | null;
  onMarkerChange: (item: MarkerItem) => void;
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
          <Box sx={{ bgcolor: "background.paper", borderRadius: 1 }}>
            {props.editingItem && (
              <MarkerGallery
                onSelectMarker={(marker) => {
                  if (props.editingItem) {
                    props.onMarkerChange({
                      ...props.editingItem,
                      marker: marker,
                    });
                  }
                }}
              />
            )}
          </Box>
        </Fade>
      )}
    </Popper>
  );
}
