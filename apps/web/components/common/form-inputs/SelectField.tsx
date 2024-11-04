import { TextField } from "@mui/material";
import MenuItem from "@mui/material/MenuItem";
import * as React from "react";
import type { Control, FieldValues, Path } from "react-hook-form";
import { Controller } from "react-hook-form";

interface RhfSelectFieldProps<O extends { value: string; label: string }, TField extends FieldValues> {
  control: Control<TField>;
  name: Path<TField>;
  required?: boolean;
  options: O[];
  label?: string;
}

export const RhfSelectField = <O extends { value: string; label: string }, TField extends FieldValues>(
  props: RhfSelectFieldProps<O, TField>
) => {
  const { control, options, name, required } = props;
  return (
    <Controller
      name={name}
      control={control}
      rules={{
        required: "this field is required",
      }}
      render={({ field, fieldState: { error } }) => {
        const { onChange, value, ref } = field;
        return (
          <TextField
            select
            value={value ?? ""}
            onChange={(event) => onChange(event.target.value)}
            inputRef={ref}
            name={name}
            required={required}
            size="medium"
            error={!!error}
            label={props.label}
            helperText={error?.message}
            SelectProps={{
              MenuProps: {
                sx: { maxHeight: "350px" },
              },
            }}>
            {options.map((option) => (
              <MenuItem key={option.value} value={option.value} sx={{ height: "32px" }}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        );
      }}
    />
  );
};
