import { Fab, Stack, Tooltip } from "@mui/material";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { makeStyles } from "@/lib/theme";
import { useMap } from "react-map-gl";

export function Zoom() {
  const { classes } = useStyles();
  const { map } = useMap();

  return (
    <>
      {map && (
        <>
          <Stack direction="column" className={classes.root}>
            <Tooltip title="Zoom In" arrow placement="left">
              <Fab onClick={() => map?.zoomIn()} size="small" className={classes.btn}>
                <Icon iconName={ICON_NAME.PLUS} fontSize="small" />
              </Fab>
            </Tooltip>
            <Tooltip title="Zoom Out" arrow placement="left">
              <Fab onClick={() => map?.zoomOut()} size="small" className={classes.btn}>
                <Icon iconName={ICON_NAME.MINUS} fontSize="small" />
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
    marginBottom: theme.spacing(1)
  },
  btn: {
    backgroundColor: theme.colors.useCases.surfaces.surface2,
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
    color: theme.isDarkModeEnabled ? "white" : theme.colors.palette.light.greyVariant4
  },
}));
