import Container from "@/components/map/panels/Container";

import Box from "@p4b/ui/components/Box";
import { Card, FormControlLabel, Radio, RadioGroup, Typography } from "@mui/material";
import { makeStyles } from "@/lib/theme";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import { useTheme } from "@p4b/ui/components/theme";
import type { MapSidebarItem } from "@/components/map/Sidebar";

interface LayerPanelProps {
  setActiveLeft: (item: MapSidebarItem | undefined) => void;
}

const LayerPanel = ({ setActiveLeft }: LayerPanelProps) => {
  const { classes } = useStyles();
  const theme = useTheme();

  return (
    <Container
      header={
        <Box className={classes.contentHeading}>
          <Typography color="#2BB381" variant="body1">
            Layer
          </Typography>
          <Icon
            iconName={ICON_NAME.CHEVRON_LEFT}
            htmlColor={theme.colors.palette.focus.main}
            fontSize="small"
            onClick={() => setActiveLeft(undefined)}
          />
        </Box>
      }
      body={
        <Card className={classes.card}>
          <RadioGroup aria-label="options" name="options">
            <FormControlLabel
              value="@content_label"
              control={<Radio />}
              label="@content_label"
              className={classes.radioLabel}
            />
          </RadioGroup>
          <Box className={classes.layerMore}>
            <Icon
              iconName={ICON_NAME.EYE}
              fontSize="small"
              htmlColor={theme.colors.palette.focus.darkVariant3}
            />
            <Icon
              iconName={ICON_NAME.MORE_VERT}
              fontSize="small"
              htmlColor={theme.colors.palette.focus.darkVariant3}
            />
          </Box>
        </Card>
      }
    />
  );
};

const useStyles = makeStyles({ name: { LayerPanel } })((theme) => ({
  contentHeading: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  card: {
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  radioLabel: {
    span: {
      fontStyle: "italic",
      fontSize: "12px",
    },
  },
  layerMore: {
    display: "flex",
  },
}));
export default LayerPanel;
