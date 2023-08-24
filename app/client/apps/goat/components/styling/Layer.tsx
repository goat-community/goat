import { setTabValue } from "@/lib/store/styling/slice";
import StarIcon from "@mui/icons-material/Star";
import {
  Radio,
  RadioGroup,
  FormControlLabel,
  Typography,
  CardContent,
  CardMedia,
  Divider,
} from "@mui/material";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import * as React from "react";
import { useDispatch, useSelector } from "react-redux";

import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import Box from "@p4b/ui/components/Box";
import { Checkbox } from "@p4b/ui/components/Checkbox";
import { MultipleSelect } from "@p4b/ui/components/Inputs/MultipleSelect";
import { Card } from "@p4b/ui/components/Surfaces";
import { IconButton, Text } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type { IStore } from "@/types/store";

function Layer() {
  const { tabValue } = useSelector((state: IStore) => state.styling);

  const dispatch = useDispatch();

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
    {
      id: 1,
      title: "Marker",
    },
    {
      id: 2,
      title: "Color",
    },
    {
      id: 3,
      title: "Stroke",
    },
    {
      id: 4,
      title: "Size",
    },
  ];

  const { classes } = useStyles();

  const handleChange = (_event: React.SyntheticEvent, newValue: any) => {
    dispatch(setTabValue(newValue));
  };

  return (
    <Box className={classes.contentInfo}>
      <Card className={classes.card}>
        <RadioGroup aria-label="options" name="options">
          <FormControlLabel
            value="@content_label"
            control={
              <Radio
                color="default"
                icon={<StarIcon className={classes.radioIcon} />}
                checkedIcon={<StarIcon className={classes.radioIconChecked} />}
              />
            }
            label="@content_label"
          />
        </RadioGroup>
      </Card>
      <Box>
        <Tabs value={tabValue} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="SIMPLE" className={classes.tab} />
          <Tab label="SMART" className={classes.tab} />
        </Tabs>
      </Box>
      {tabValue === 0 ? (
        <>
          <Card>
            <CardMedia className={classes.media} component="div" />
            <CardContent className={classes.content}>
              <IconButton type="submit" size="small" iconId="info" className={classes.contentButton} />
              <Typography variant="body2" color="text.secondary">
                Location (single symbol)
              </Typography>
              <Checkbox />
            </CardContent>
          </Card>
          {layerAccordionInfo.map((item) => (
            <Box key={item.id}>
              <BasicAccordion title={item.title} variant="secondary" className={classes.accordion}>
                <div>Lorem</div>
                <div>Lorem</div>
                <div>Lorem</div>
              </BasicAccordion>
              <Divider className={classes.divider} />
            </Box>
          ))}
        </>
      ) : (
        <>
          <Box className={classes.attributeContainer}>
            <Typography variant="body2">Attribute</Typography>
            <MultipleSelect options={layerTypes} label="Browser layer attributes" />
          </Box>
          <Box>
            <Text color="secondary" typo="label 2" className={classes.descriptionText}>
              Style your map according to the values of a specific attribute or column in the dataset, using
              techniques such as color coding or symbol size variation for categorical and numerical data.
            </Text>
          </Box>
        </>
      )}
    </Box>
  );
}

const useStyles = makeStyles({ name: { Layer } })((theme) => ({
  contentInfo: {
    display: "flex",
    flexDirection: "column",
    rowGap: "24px",
    padding: "16px",
  },
  descriptionText: {
    fontStyle: "italic",
    margin: "0  8px",
  },
  tab: {
    width: "50%",
  },
  attributeContainer: {
    display: "flex",
    flexDirection: "column",
    rowGap: "8px",
  },
  card: {
    paddingLeft: theme.spacing(2),
  },
  radioIcon: {
    color: "#2BB3814D",
  },
  radioIconChecked: {
    color: "#2BB381",
  },
  media: {
    height: "42px",
    backgroundColor: "#2bb3810a",
    border: "none",
  },
  content: {
    display: "flex",
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
    borderBottom: "1px solid #2bb3814d",
  },
}));
export default Layer;
