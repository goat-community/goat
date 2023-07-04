// Copyright (c) 2020 GitHub user u/garronej
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import type { SelectChangeEvent } from "@mui/material/Select";
import { forwardRef, memo } from "react";
import * as React from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";

export type SelectFieldProps = {
  className?: string;
  updateChange?: (value: string) => void;
  options: { name: string; value: string }[];
  defaultValue: string;
  label: string;
  size: "small" | "medium";
};

export const SelectField = memo(
  forwardRef<any, SelectFieldProps>((props, ref) => {
    const {
      className,
      updateChange,
      options,
      defaultValue,
      label,
      size = "medium",
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;
    const [values, setValues] = React.useState("");

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes, cx } = useStyles();

    const handleChange = (event: SelectChangeEvent) => {
      if (updateChange) {
        updateChange(event.target.value as string);
      }
      setValues(event.target.value as string);
    };

    return (
      <>
        <Box sx={{ minWidth: 120 }}>
          <FormControl fullWidth>
            <InputLabel id="demo-simple-select-label">{label}</InputLabel>
            <Select
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              value={values ? values : defaultValue}
              label={label}
              size={size}
              onChange={handleChange}>
              {options.map((option) => (
                <MenuItem value={option.value} key={option.value}>
                  {option.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </>
    );
  })
);

const useStyles = makeStyles({ name: { SelectField } })((theme) => ({}));
