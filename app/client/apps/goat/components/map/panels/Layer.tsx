import Container from "@/components/map/panels/Container";

import { Text } from "@p4b/ui/components/theme";
import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";
import { makeStyles } from "@/lib/theme";
import { Card, IconButton, Stack, Typography } from "@mui/material";
import type { LayerProps, SourceProps } from "@/types/map/layers";

interface PanelProps {
  onCollapse?: () => void;
  layers?: (SourceProps & LayerProps)[];
}

const LayerPanel = ({ onCollapse, layers }: PanelProps) => {
  const { classes } = useStyles();

  return (
    <Container
      header={
        <>
          <Text typo="page heading">Layers</Text>
          {onCollapse && (
            <IconButton
              onClick={onCollapse}
              type="button"
              className={classes.iconButton}
            >
              <Icon
                iconName={ICON_NAME.CHEVRON_LEFT}
                fontSize="small"
                className={classes.icon}
              />
            </IconButton>
          )}
        </>
      }
      body={
        <>
          {layers?.map((layer) => (
            <Card
              key={layer.id}
              sx={{
                boxShadow: "0px 1px 10px 0px rgba(0, 0, 0, 0.06), 0px 2px 2px 0px rgba(0, 0, 0, 0.07), 0px 1px 2px -1px rgba(0, 0, 0, 0.10)",
                borderRadius: 0,
                ":hover": {
                  boxShadow: "0px 1px 10px 0px rgba(0, 0, 0, 0.12), 0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 2px 4px -1px rgba(0, 0, 0, 0.20)",
                },
                cursor: "pointer",
              }}
              variant="outlined"
              className={classes.layerCard}
            >
              <Stack
                spacing={1}
                direction="row"
                alignItems="center"
                justifyContent="space-between"
              >
                <Typography noWrap variant="body2">
                  {layer.name}
                </Typography>
                <Stack direction="row" spacing={1}>
                  <IconButton
                    type="button"
                    size="small"
                    className={classes.iconButton}
                  >
                    <Icon
                      iconName={layer.active ? ICON_NAME.EYE : ICON_NAME.EYE_SLASH}
                      fontSize="small"
                      className={classes.icon}
                    />
                  </IconButton>
                </Stack>
              </Stack>
            </Card>
          ))}
        </>
      }
    />
  );
};

const useStyles = makeStyles()((theme) => ({
  root: {},
  btn: {
    backgroundColor: theme.colors.useCases.surfaces.surface2,
    color: theme.isDarkModeEnabled
      ? "white"
      : theme.colors.palette.light.greyVariant4,
  },
  iconButton: {
    padding: theme.spacing(1),
  },
  popper: {},
  icon: {
    color: theme.isDarkModeEnabled
      ? "white"
      : theme.colors.palette.light.greyVariant2,
    margin: theme.spacing(2),
    "&:hover": {
      color: theme.colors.palette.focus.main,
    },
  },
  layerCard: {
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    paddingTop: theme.spacing(0),
    paddingBottom: theme.spacing(0),
    margin: theme.spacing(1),
  },
}));

export default LayerPanel;
