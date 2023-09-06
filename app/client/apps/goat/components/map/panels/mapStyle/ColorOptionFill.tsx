import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { makeStyles } from "@/lib/theme";
import Box from "@p4b/ui/components/Box";
import { Divider, TextField, Typography } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";
import {
  setLayerFillColor,
  setLayerFillOutLineColor,
} from "@/lib/store/styling/slice";
import { useAppDispatch } from "@/hooks/useAppDispatch";
import { selectMapLayer } from '@/lib/store/styling/selectors'

const ColorOptionFill = () => {
  const mapLayer = useSelector(selectMapLayer)

  const { classes } = useStyles();
  const dispatch = useAppDispatch();

  const handleFillColorChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    dispatch(setLayerFillColor({ key: "fill-color", val: event.target.value }));
  };

  const handleStrokeColorChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    dispatch(setLayerFillOutLineColor(event.target.value));
  };

  // const handleFillOpacityChange = (
  //   event: React.ChangeEvent<HTMLInputElement>,
  // ) => {
  //   setFillOpacity(event.target.value);
  // };

  // const handleStrokeOpacityChange = (
  //   esvent: React.ChangeEvent<HTMLInputElement>,
  // ) => {
  //   setStrokeOpacity(event.target.value);
  // };

  return (
    <BasicAccordion title="Color" variant="secondary">
      <Box className={classes.root}>
        <Box className={classes.colorContainer}>
          <Typography variant="body1">Fill</Typography>
          <Box className={classes.inputsContainer}>
            <TextField
              type="color"
              size="small"
              className={classes.inputs}
              value={mapLayer?.paint ? mapLayer?.paint["fill-color"] : "#000"}
              onChange={handleFillColorChange}
            />
            {/*<TextField*/}
            {/*  type="number"*/}
            {/*  size="small"*/}
            {/*  className={classes.inputs}*/}
            {/*  value={fillOpacity}*/}
            {/*  onChange={handleFillOpacityChange}*/}
            {/*/>*/}
          </Box>
        </Box>
        <Divider className={classes.divider} />
        <Box className={classes.colorContainer}>
          <Typography variant="body1">Stroke</Typography>
          <Box className={classes.inputsContainer}>
            <TextField
              type="color"
              size="small"
              className={classes.inputs}
              value={
                mapLayer?.paint ? mapLayer?.paint["fill-outline-color"] : "#000"
              }
              onChange={handleStrokeColorChange}
            />
            {/*<TextField*/}
            {/*  type="number"*/}
            {/*  size="small"*/}
            {/*  className={classes.inputs}*/}
            {/*  value={strokeOpacity}*/}
            {/*  onChange={handleStrokeOpacityChange}*/}
            {/*/>*/}
          </Box>
        </Box>
      </Box>
    </BasicAccordion>
  );
};

const useStyles = makeStyles({ name: { ColorOptionFill } })((theme) => ({
  root: {
    display: "flex",
    flexDirection: "column",
    rowGap: "16px",
  },
  colorContainer: {
    display: "flex",
    flexDirection: "column",
    rowGap: "8px",
  },
  inputsContainer: {
    display: "flex",
    columnGap: "4px",
  },
  inputs: {
    width: "50%",
    "& .MuiInputBase-root": {
      height: "32px",
      padding: "2px 8px",
    },
    input: {
      padding: "unset",
      height: "100%",
    },
  },
  divider: {
    width: "100%",
    borderTop: "none",
    borderBottom: `1px solid ${theme.colors.palette.focus}`,
  },
}));

export default ColorOptionFill;
