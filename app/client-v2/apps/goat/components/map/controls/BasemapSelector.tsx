import { ArrowPopper } from "@/components/ArrowPoper";
import { ListTile } from "@/components/common/ListTile";
import { makeStyles } from "@/lib/theme";
import { Close } from "@mui/icons-material";
import MapIcon from "@mui/icons-material/Map";
import { Box, IconButton, Paper, Tooltip, Typography } from "@mui/material";
import Fab from "@mui/material/Fab";
import { useEffect, useState } from "react";

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

  return (
    <>
      <ArrowPopper
        placement="top-end"
        content={
          <Paper sx={{ width: 360, overflow: "auto" }}>
            <Box position="absolute" top={5} right={5}>
              <IconButton onClick={() => setOpen(false)}>
                <Close />
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
          <Fab onClick={() => setOpen(!open)} size="large">
            <MapIcon />
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
}));
