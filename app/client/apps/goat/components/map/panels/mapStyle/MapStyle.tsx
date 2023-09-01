import Container from "@/components/map/panels/Container";
import { IconButton, Text, useTheme } from "@p4b/ui/components/theme";
import {
  Button,
  CardContent,
  CardMedia,
  Divider,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from "@mui/material";
import { makeStyles } from "@/lib/theme";
import { useDispatch, useSelector } from "react-redux";
import type { IStore } from "@/types/store";
import {
  addMarker,
  resetStyles,
  saveStyles,
  setTabValue,
} from "@/lib/store/styling/slice";
import { Card } from "@p4b/ui/components/Surfaces";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { Checkbox } from "@p4b/ui/components/Checkbox";
import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { MultipleSelect } from "@p4b/ui/components/Inputs/MultipleSelect";
import Box from "@p4b/ui/components/Box";
import type { MapSidebarItem } from "@/components/map/Sidebar";
import { Icon, ICON_NAME } from "@p4b/ui/components/Icon";
import React from "react";
import { v4 } from "uuid";
// import Size from "@/components/map/panels/mapStyle/Size";
import Color from "@/components/map/panels/mapStyle/Color";
// import Marker from "@/components/map/panels/mapStyle/Marker";

interface MapStyleProps {
  setActiveRight: (item: MapSidebarItem | undefined) => void;
}

const layerTypes = [
  {
    label: "@column_label",
    value: "@column_label",
  },
  {
    label: "@column_label1",
    value: "@column_label1",
  },
];

const layerAccordionInfo = [
  // {
  //   id: 1,
  //   title: "Marker",
  //   values: ["LOCATION", "CROSS"],
  // },
  // {
  //   id: 2,
  //   title: "Color",
  //   values: [],
  // },
  {
    id: 3,
    title: "Stroke",
    values: [],
  },
  // {
  //   id: 4,
  //   title: "Size",
  //   values: [],
  // },
];

const MapStylePanel = ({ setActiveRight }: MapStyleProps) => {
  const { tabValue, initialViewState } = useSelector(
    (state: IStore) => state.styling,
  );

  const dispatch = useDispatch();
  const { classes } = useStyles();
  const theme = useTheme();

  const handleChange = (_: React.SyntheticEvent, newValue: number) => {
    dispatch(setTabValue(newValue));
  };

  const resetStylesHandler = () => {
    dispatch(resetStyles());
  };

  const saveStylesHandler = () => {
    dispatch(saveStyles());
  };

  const addMarkerHandler = (name: string) => {
    dispatch(
      addMarker({
        id: v4(),
        lat: initialViewState.latitude,
        long: initialViewState.longitude,
        iconName: name,
      }),
    );
  };

  return (
    <Container
      header={
        <Box className={classes.contentHeading}>
          <Icon
            iconName={ICON_NAME.CHEVRON_RIGHT}
            htmlColor={theme.colors.palette.focus.main}
            fontSize="small"
            onClick={() => setActiveRight(undefined)}
          />
          <Typography color={theme.colors.palette.focus.main} variant="body1">
            Layer design
          </Typography>
        </Box>
      }
      body={
        <Box className={classes.contentInfo}>
          <Card className={classes.card}>
            <RadioGroup aria-label="options" name="options">
              <FormControlLabel
                value="@content_label"
                className={classes.radioLabel}
                control={
                  <Radio
                    color="default"
                    icon={
                      <Icon
                        iconName={ICON_NAME.STAR}
                        htmlColor={theme.colors.palette.focus.darkVariant3}
                        fontSize="small"
                      />
                    }
                    checkedIcon={
                      <Icon
                        iconName={ICON_NAME.STAR}
                        htmlColor={theme.colors.palette.focus.main}
                        fontSize="small"
                      />
                    }
                  />
                }
                label="@content_label"
              />
            </RadioGroup>
          </Card>
          <Box>
            <Tabs
              value={tabValue}
              onChange={handleChange}
              aria-label="basic tabs example"
            >
              <Tab label="SIMPLE" className={classes.tab} />
              <Tab label="SMART" className={classes.tab} />
            </Tabs>
          </Box>
          {tabValue === 0 ? (
            <>
              <Card>
                <CardMedia className={classes.media} component="div" />
                <CardContent className={classes.content}>
                  <IconButton
                    type="submit"
                    size="small"
                    iconId="info"
                    className={classes.contentButton}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Location (single symbol)
                  </Typography>
                  <Checkbox />
                </CardContent>
              </Card>
              {layerAccordionInfo.map((item) => (
                <Box key={item.id}>
                  <BasicAccordion
                    title={item.title}
                    variant="secondary"
                    className={classes.accordion}
                  >
                    {item?.values?.map((val) => (
                      <Icon
                        key={v4()}
                        iconName={ICON_NAME[val]}
                        fontSize="small"
                        onClick={() => addMarkerHandler(val)}
                      />
                    ))}
                  </BasicAccordion>
                  <Divider className={classes.divider} />
                </Box>
              ))}
              {/*<Marker />*/}
              {/*<Size />*/}
              <Color />
            </>
          ) : (
            <>
              <Box className={classes.attributeContainer}>
                <Typography variant="body2">Attribute</Typography>
                <MultipleSelect
                  options={layerTypes}
                  label="Browser layer attributes"
                />
              </Box>
              <Box>
                <Text
                  color="secondary"
                  typo="label 2"
                  className={classes.descriptionText}
                >
                  Style your map according to the values of a specific attribute
                  or column in the dataset, using techniques such as color
                  coding or symbol size variation for categorical and numerical
                  data.
                </Text>
              </Box>
            </>
          )}
        </Box>
      }
      action={
        <Box className={classes.buttonsContainer}>
          <Button
            className={classes.button}
            color="secondary"
            variant="outlined"
            onClick={resetStylesHandler}
          >
            Reset
          </Button>
          <Button
            className={classes.button}
            color="primary"
            variant="outlined"
            onClick={saveStylesHandler}
            endIcon={
              <Icon iconName={ICON_NAME.CHEVRON_DOWN} fontSize="small" />
            }
          >
            Save As
          </Button>
        </Box>
      }
    />
  );
};

const useStyles = makeStyles({ name: { MapStylePanel } })((theme) => ({
  contentHeading: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
  },
  buttonsContainer: {
    minWidth: "266px",
    display: "flex",
    columnGap: "16px",
  },
  button: {
    borderRadius: "24px",
    textTransform: "none",
    fontSize: "14px",
    width: "50%",
    "&:disabled": {
      border: "1px solid #ccc",
      color: theme.colors.palette.light.greyVariant4,
    },
  },
  contentInfo: {
    display: "flex",
    flexDirection: "column",
    rowGap: "24px",
  },
  descriptionText: {
    fontStyle: "italic",
    margin: "0 8px",
  },
  tab: {
    width: "50%",
  },
  attributeContainer: {
    display: "flex",
    flexDirection: "column",
    rowGap: "8px",
    width: "100%",
  },
  card: {
    paddingLeft: theme.spacing(2),
  },
  media: {
    height: "42px",
    backgroundColor: theme.colors.palette.focus.darkVariant2,
    border: "none",
  },
  content: {
    display: "flex",
    columnGap: "6px",
    padding: "8px 16px",
  },
  contentButton: {
    alignSelf: "flex-start",
  },
  accordion: {
    "& .MuiPaper-root": {
      boxShadow: "unset",
    },
  },
  divider: {
    width: "100%",
    borderTop: "none",
    borderBottom: `1px solid ${theme.colors.palette.focus}`,
  },
  radioLabel: {
    span: {
      fontSize: "12px",
      fontStyle: "italic",
    },
  },
}));

export default MapStylePanel;
