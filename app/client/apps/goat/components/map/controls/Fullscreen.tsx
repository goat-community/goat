import { Fab, Stack, Tooltip } from "@mui/material";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { makeStyles } from "@/lib/theme";
import { useMap } from "react-map-gl";
import { useState } from "react";
import screenfull from "screenfull";

export function Fullscren() {
  const [fullscreen, setFullscreen] = useState(screenfull.isFullscreen);
  const { classes } = useStyles();
  const { map } = useMap();
  if (screenfull.isEnabled) {
    screenfull.on("change", () => {
      setFullscreen(screenfull.isFullscreen);
    });
  }
  const toggleFullscreen = () => {
    if (screenfull.isEnabled) {
      screenfull.toggle();
    }
  };
  return (
    <>
      {map && (
        <>
          <Stack direction="column" className={classes.root}>
            <Tooltip title={fullscreen ? "Exit Fullscreen" : "Fullscreen"} arrow placement="left">
              <Fab onClick={() => toggleFullscreen()} size="small" className={classes.btn}>
                <Icon iconName={fullscreen ? ICON_NAME.MINIMIZE : ICON_NAME.MAXIMIZE} fontSize="small" />
              </Fab>
            </Tooltip>
          </Stack>
        </>
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
  btn: {
    backgroundColor: theme.colors.useCases.surfaces.surface2,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
    color: theme.isDarkModeEnabled ? "white" : theme.colors.palette.light.greyVariant4,
  },
}));
