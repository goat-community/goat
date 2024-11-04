import { FormControl, MenuItem, TextField, Typography, useTheme } from "@mui/material";
import Autocomplete, { createFilterOptions } from "@mui/material/Autocomplete";
import { useState } from "react";

import type { SelectorItem } from "@/types/map/common";

import FormLabelHelper from "@/components/common/FormLabelHelper";

interface SelectorFreeSoloProps {
  label?: string;
  tooltip?: string;
  placeholder?: string;
  disabled?: boolean;
  options: SelectorItem[];
  selectedItem: SelectorItem | undefined;
  onClear?: () => void;
  onSelect?: (value: SelectorItem | undefined) => void;
  inputType?: "number" | "text";
}

const filter = createFilterOptions<SelectorItem>();

const SelectorFreeSolo = (props: SelectorFreeSoloProps) => {
  const theme = useTheme();
  const [focused, setFocused] = useState(false);
  return (
    <FormControl size="small" fullWidth>
      {props.label && (
        <FormLabelHelper
          label={props.label}
          color={
            props.disabled ? theme.palette.secondary.main : focused ? theme.palette.primary.main : "inherit"
          }
          tooltip={props.tooltip}
        />
      )}

      <Autocomplete
        freeSolo
        disabled={props.disabled}
        options={props.options}
        value={props.selectedItem}
        onFocus={() => {
          setFocused(true);
        }}
        onBlur={() => setFocused(false)}
        size="small"
        onChange={(_event, newValue) => {
          if (typeof newValue === "string") {
            props.onSelect?.({
              value: newValue,
              label: newValue,
            });
          } else if (typeof newValue === "object" && newValue !== null) {
            // Create a new value from the user input
            props.onSelect?.(newValue);
          } else {
            props.onSelect?.(undefined);
          }
        }}
        filterOptions={(options, params) => {
          const filtered = filter(options, params);
          const { inputValue } = params;
          // Suggest the creation of a new value
          const isExisting = options.some((option) => inputValue === option.label);
          if (inputValue !== "" && !isExisting) {
            filtered.push({
              value: inputValue,
              label: inputValue,
            });
          }

          return filtered;
        }}
        renderOption={(props, option) => (
          <MenuItem {...props} key={option.value}>
            <Typography
              variant="body2"
              fontWeight="bold"
              style={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}>
              {option.label}
            </Typography>
          </MenuItem>
        )}
        renderInput={(params) => (
          <TextField
            type={props.inputType || "text"}
            sx={{
              "& input::placeholder": {
                fontSize: "0.875rem",
              },
            }}
            placeholder={props.placeholder}
            {...params}
          />
        )}
      />
    </FormControl>
  );
};

export default SelectorFreeSolo;
