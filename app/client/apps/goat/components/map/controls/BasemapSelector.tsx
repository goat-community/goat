import { ArrowPopper } from "@/components/ArrowPoper";
import { ListTile } from "@/components/common/ListTile";
import { makeStyles, useTheme } from "@/lib/theme";
import { Box, IconButton, Paper, Stack, Tooltip } from "@mui/material";
import Fab from "@mui/material/Fab";
import { useState } from "react";

import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { Text } from "@p4b/ui/components/theme";
import { useMap } from "react-map-gl";

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
  active: number[];
  basemapChange: (styleIndex: number[]) => void;
}

export function BasemapSelector(props: BasemapSelectorProps) {
  const [open, setOpen] = useState(false);
  const { styles, active, basemapChange } = props;
  const { classes } = useStyles();
  const theme = useTheme();
  const { map } = useMap();

  return (
    <>
      {map && (
        <Stack direction="column" className={classes.root}>
          <ArrowPopper
            placement="top-end"
            content={
              <Paper sx={{ width: 360, overflow: "auto" }}>
                <Box position="absolute" top={5} right={5}>
                  <IconButton onClick={() => setOpen(false)}>
                    <Icon
                      iconName={ICON_NAME.CLOSE}
                      htmlColor={theme.isDarkModeEnabled ? "white" : "gray"}
                      fontSize="small"
                    />
                  </IconButton>
                </Box>

                <Text typo="page heading" className={classes.title}>
                  Map Style
                </Text>
                <ListTile
                  items={styles}
                  selected={active}
                  thumbnailBorder="rounded"
                  onChange={(selectedStyleIndex) => {
                    basemapChange(selectedStyleIndex);
                  }}
                />
              </Paper>
            }
            open={open}
            arrow={true}
            onClose={() => setOpen(false)}
          >
            <Tooltip title="Basemaps" arrow placement="left">
              <Fab onClick={() => setOpen(!open)} size="large" className={classes.btn}>
                <Icon iconName={ICON_NAME.MAP} fontSize="small" />
              </Fab>
            </Tooltip>
          </ArrowPopper>
        </Stack>
      )}
    </>
  );
}

const useStyles = makeStyles()((theme) => ({
  root: {
    alignItems: "flex-end",
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  title: {
    margin: theme.spacing(3),
  },
  btn: {
    backgroundColor: theme.colors.useCases.surfaces.surface2,
    color: theme.isDarkModeEnabled ? "white" : theme.colors.palette.light.greyVariant4,
  },
}));
