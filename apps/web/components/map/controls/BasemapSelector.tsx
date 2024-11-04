// import { makeStyles, useTheme } from "@/lib/theme";
import { Box, IconButton, Paper, Stack, Tooltip, Typography, useTheme } from "@mui/material";
import Fab from "@mui/material/Fab";
import { useMemo, useState } from "react";
import { useMap } from "react-map-gl/maplibre";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import { ArrowPopper } from "@/components/ArrowPoper";
import { ListTile } from "@/components/common/ListTile";

interface Item {
  value: string;
  url: string;
  title: string;
  subtitle: string;
  thumbnail: string;
  attributionComponent?: React.ReactNode;
}

interface BasemapSelectorProps {
  styles: Item[];
  active: string;
  basemapChange: (style: string) => void;
}

export function BasemapSelector(props: BasemapSelectorProps) {
  const { t } = useTranslation("common");
  const [open, setOpen] = useState(false);
  const { styles, active, basemapChange } = props;
  const activeIndex = useMemo(() => {
    return styles.findIndex((style) => style.value === active);
  }, [styles, active]);
  const theme = useTheme();
  const { map } = useMap();

  return (
    <>
      {map && (
        <Stack
          direction="column"
          sx={{
            alignItems: "flex-end",
            marginTop: theme.spacing(1),
            marginBottom: theme.spacing(1),
          }}>
          <ArrowPopper
            placement="top-end"
            content={
              <Paper sx={{ width: 360, overflow: "auto" }}>
                <Box position="absolute" top={5} right={5}>
                  <IconButton onClick={() => setOpen(false)}>
                    <Icon
                      iconName={ICON_NAME.CLOSE}
                      htmlColor={theme.palette.text.secondary}
                      fontSize="small"
                    />
                  </IconButton>
                </Box>

                <Typography variant="body1" fontWeight="bold" sx={{ margin: theme.spacing(3) }}>
                  {t("map_style")}
                </Typography>
                <ListTile
                  items={styles}
                  selected={[activeIndex]}
                  thumbnailBorder="rounded"
                  onChange={(selectedStyleIndex) => {
                    const basemapValue = styles[selectedStyleIndex[0]].value;
                    basemapChange(basemapValue);
                  }}
                />
              </Paper>
            }
            open={open}
            arrow={true}
            onClose={() => setOpen(false)}>
            <Tooltip title={t("basemaps")} arrow placement="left">
              <Fab
                onClick={() => setOpen(!open)}
                size="large"
                sx={{
                  backgroundColor: theme.palette.background.paper,
                  color: theme.palette.text.secondary,
                  ...(open && {
                    color: theme.palette.primary.main,
                  }),
                  "&:hover": {
                    backgroundColor: theme.palette.background.default,
                  },
                }}>
                <Icon iconName={ICON_NAME.MAP} fontSize="small" htmlColor="inherit" />
              </Fab>
            </Tooltip>
          </ArrowPopper>
        </Stack>
      )}
    </>
  );
}
