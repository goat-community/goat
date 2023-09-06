import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { makeStyles } from "@/lib/theme";
import Box from "@p4b/ui/components/Box";
import { TextField, Typography } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";
import { setLayerFillColor } from "@/lib/store/styling/slice";
import { useAppDispatch } from "@/hooks/useAppDispatch";
import { selectMapLayer } from "@/lib/store/styling/selectors";

const ColorOptionLine = () => {
  const mapLayer = useSelector(selectMapLayer);

  const { classes } = useStyles();
  const dispatch = useAppDispatch();

  const handleFillColorChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    dispatch(setLayerFillColor({ key: "line-color", val: event.target.value }));
  };

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
              value={mapLayer?.paint?.["line-color"]}
              onChange={handleFillColorChange}
            />
          </Box>
        </Box>
      </Box>
    </BasicAccordion>
  );
};

const useStyles = makeStyles({ name: { ColorOptionLine } })(() => ({
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
}));

export default ColorOptionLine;
