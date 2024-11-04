import { Box, Divider, Paper, Stack, Typography } from "@mui/material";

import { MAKI_ICONS_BASE_URL, MAKI_ICON_SIZE, MAKI_ICON_TYPES } from "@/lib/constants/icons";

import { MaskedImageIcon } from "@/components/map/panels/style/other/MaskedImageIcon";

type MarkerGalleryProps = {
  onSelectMarker?: (marker: { name: string; url: string }) => void;
};

const MarkerGallery = (props: MarkerGalleryProps) => {
  return (
    <Paper
      sx={{
        boxShadow: "rgba(0, 0, 0, 0.16) 0px 6px 12px 0px",
        width: "235px",
        maxHeight: "500px",
      }}>
      <Box
        sx={{
          maxHeight: "280px",
          overflowY: "auto",
          p: 2,
          justifyContent: "center",
        }}>
        {MAKI_ICON_TYPES.map((group) => (
          <Stack key={group.name} direction="column" sx={{ mb: 2 }} spacing={2}>
            <Stack>
              <Typography variant="body2" fontWeight="bold">
                {group.name}
              </Typography>
              <Divider sx={{ mb: 1 }} />
            </Stack>
            <div>
              {group.icons.map((icon) => (
                <div
                  style={{
                    cursor: "pointer",
                    margin: "5px",
                    display: "inline-flex",
                  }}
                  onClick={() => {
                    props.onSelectMarker?.({
                      name: icon,
                      url: `${MAKI_ICONS_BASE_URL}/${icon}.svg`,
                    });
                  }}
                  key={icon}>
                  <MaskedImageIcon
                    imageUrl={`${MAKI_ICONS_BASE_URL}/${icon}.svg`}
                    dimension={`${MAKI_ICON_SIZE}px`}
                  />
                </div>
              ))}
            </div>
          </Stack>
        ))}
      </Box>
    </Paper>
  );
};

export default MarkerGallery;
