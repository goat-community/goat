import React, { useState } from "react";
import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { Slider, TextField } from "@mui/material";
import { makeStyles } from "@/lib/theme";
import Box from "@p4b/ui/components/Box";

const Stroke = () => {
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
        <Box className={classes.optionContainer}>
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
      </BasicAccordion>
    </div>
  );
};

const useStyles = makeStyles({ name: { Stroke } })((theme) => ({
  optionContainer: {
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
}));

export default Stroke;
