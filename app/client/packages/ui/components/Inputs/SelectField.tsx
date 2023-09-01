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

import { Checkbox } from "../Checkbox";

export type SelectFieldProps = {
  className?: string;
  updateChange?: ((value: string | string[]) => void);
  options: { name: React.ReactNode; value: string }[];
  defaultValue?: string | string[];
  label: string;
  size: "small" | "medium";
  multiple?: boolean;
  checkbox?: boolean;
  disabled?: boolean;
};

/**
 * A memoized functional component that renders a select field.
 * @param {SelectFieldProps} props - The props for the select field.
 * @param {React.Ref<any>} ref - The ref for the select field.
 * @returns The rendered select field component.
 */

export const SelectField = memo(
  forwardRef<any, SelectFieldProps>((props) => {
    const {
      className,
      updateChange,
      disabled = false,
      options,
      label,
      size = "medium",
      multiple = false,
      checkbox = false,
      defaultValue = "",
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    // Component State
    const [values, setValues] = React.useState<string | string[]>(
      multiple ? [] : "",
    );

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    // functions
    const handleChange = (event: SelectChangeEvent) => {
      if (updateChange && !multiple) {
        if(typeof event.target.value){
          updateChange(event.target.value);
        }
      } else if (updateChange && multiple) {
        const value = event.target.value as string;
        const valueArr = value.split(", ");
        updateChange(valueArr);
      }
      setValues(event.target.value as string);
    };

    return (
      <>
        <Box sx={{ minWidth: 120 }} className={className}>
          <FormControl fullWidth size={size}>
            <InputLabel id="demo-simple-select-label">{label}</InputLabel>
            <Select
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              disabled={disabled}
              value={values && !Array.isArray(values) ? values : defaultValue}
              label={label}
              multiple={multiple}
              // MenuProps={multiple ? MenuProps : undefined}
              renderValue={
                multiple
                  ? (selected) => [selected].flat().join(", ")
                  : (value) => value
              }
              onChange={handleChange}
            >
              {options.map((option) => (
                <MenuItem value={option.value} key={option.value}>
                  {checkbox ? (
                    <Checkbox checked={values.indexOf(option.value) > -1} />
                  ) : null}
                  {option.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </>
    );
  }),
);
