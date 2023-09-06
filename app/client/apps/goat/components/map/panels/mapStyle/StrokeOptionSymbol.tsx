import React, { useState } from "react";
import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { Divider, Select, Slider, TextField, Typography } from "@mui/material";
import { makeStyles } from "@/lib/theme";
import Box from "@p4b/ui/components/Box";

const StrokeOptionSymbol = () => {
  const [width, setWidth] = useState<number>(20);

  const { classes } = useStyles();
  const handleSliderChange = (_: Event, newValue: number | number[]) => {
    if (typeof newValue === "number") {
      setWidth(newValue);
    }
  };

  const handleTextFieldChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const newValue = parseFloat(event.target.value);
    if (!isNaN(newValue)) {
      setWidth(newValue);
    }
  };

  return (
    <div>
      <BasicAccordion title="Stroke" variant="secondary">
        <Box className={classes.root}>
          <Box className={classes.optionContainer}>
            <Typography variant="body2">Width</Typography>
            <Box className={classes.sizePickerContainer}>
              <TextField
                type="number"
                size="small"
                value={width.toString()}
                onChange={handleTextFieldChange}
              />
              <Slider
                value={width}
                onChange={handleSliderChange}
                aria-label="Small"
                valueLabelDisplay="auto"
                color="primary"
                className={classes.slider}
              />
            </Box>
          </Box>
          <Divider className={classes.divider} />
          <Box className={classes.optionContainer}>
            <Typography variant="body2">Style</Typography>
            <Select size="small" />
          </Box>
        </Box>
      </BasicAccordion>
    </div>
  );
};

const useStyles = makeStyles({ name: { StrokeOptionSymbol } })((theme) => ({
  root: {
    display: "flex",
    flexDirection: "column",
    rowGap: "16px",
  },
  optionContainer: {
    display: "flex",
    flexDirection: "column",
    rowGap: "16px",
  },
  sizePickerContainer: {
    display: "flex",
    flexDirection: "column",
    rowGap: "45px",
  },
  slider: {
    "& .MuiSlider-valueLabel": {
      lineHeight: 1.2,
      fontSize: 12,
      background: "unset",
      padding: 0,
      width: 31,
      height: 30,
      backgroundColor: theme.colors.palette.light.main,
      color: theme.colors.palette.focus.main,
    },
  },
  divider: {
    width: "100%",
    borderTop: "none",
    borderBottom: `1px solid ${theme.colors.palette.focus}`,
  },
}));

export default StrokeOptionSymbol;
