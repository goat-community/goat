import { ArrowPopper } from "@/components/ArrowPoper";
import { ListTile } from "@/components/common/ListTile";
import { makeStyles, useTheme } from "@/lib/theme";
import { Close } from "@mui/icons-material";
import { Box, IconButton, Paper, Tooltip, Typography } from "@mui/material";
import Fab from "@mui/material/Fab";
import { useState } from "react";

import { FaIcon, ICON_NAME } from "@p4b/ui/components/DataDisplay/FAIcon";
import { Text } from "@p4b/ui/components/theme";

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

  return (
    <>
      <ArrowPopper
        placement="top-end"
        content={
          <Paper sx={{ width: 360, overflow: "auto" }}>
            <Box position="absolute" top={5} right={5}>
              <IconButton onClick={() => setOpen(false)}>
                <FaIcon
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
        onClose={() => setOpen(false)}>
        <Tooltip title="Basemaps" arrow placement="left">
          <Fab onClick={() => setOpen(!open)} size="large" className={classes.btn}>
            <FaIcon iconName={ICON_NAME.MAP} fontSize="small" />
          </Fab>
        </Tooltip>
      </ArrowPopper>
      ;
    </>
  );
}

const useStyles = makeStyles()((theme) => ({
  title: {
    margin: theme.spacing(3),
  },
  btn: {
    backgroundColor: theme.colors.useCases.surfaces.surface2,
  },
}));
