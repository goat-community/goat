import CheckBoxIcon from "@mui/icons-material/CheckBox";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import * as React from "react";

import type { Option } from "../../../types/atomicComponents/index";
import { makeStyles } from "../../lib/ThemeProvider";
import { Checkbox } from "../Checkbox";

interface CustomMultiAutocompleteProps {
  options: Option[];
}

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

interface AutoComplete {
  className?: string;
  label?: string;
  size: "small" | "medium";
  options?: { label: React.ReactNode; value: string }[];
  multiple?: boolean;
  setSelected?: (value: Option[]) => void;
  selectedOptions?: Option[];
}

export function AutoComplete(props: AutoComplete) {
  const {
    className,
    label = "",
    size = "small",
    options = [],
    multiple = false,
    setSelected,
    selectedOptions,
  } = props;

  const inputRef = React.useRef<HTMLInputElement | null>(null);

  const handleChange = (event: React.SyntheticEvent, value: Option[]) => {
    if (setSelected) {
      setSelected([
        ...value.map((val) => {
          const newVal = val;
          newVal.selected = true;
          return newVal;
        }),
      ]);
    }
  };

  // Create a function to get the selected options based on the selectedOptionValues
  const getSelectedOptions = () =>
    options.filter(
      (option) => selectedOptions && selectedOptions.some((vendor) => vendor.label === option.label)
    );

  return (
    <>
      <Autocomplete
        className={className}
        multiple={multiple}
        options={options}
        disableCloseOnSelect
        size={size}
        renderOption={(props, option, { selected }) => (
          <li {...props} key={option.value}>
            <Checkbox checked={selected} icon={icon} checkedIcon={checkedIcon} />
            {option.label}
          </li>
        )}
        renderInput={(params) => (
          <TextField
            {...params}
            variant="outlined"
            label={label}
            placeholder="Select Options"
            inputRef={inputRef}
          />
        )}
        onChange={handleChange}
        value={getSelectedOptions()}
        renderTags={() => null}
      />
    </>
  );
}

const useStyles = makeStyles({ name: { AutoComplete } })((theme) => ({
  checkbox: {
    marginRight: 8,
  },
}));
