import CheckBoxIcon from "@mui/icons-material/CheckBox";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import * as React from "react";

import { Checkbox } from "../Checkbox";

type Option = {
  label: React.ReactNode;
  value: string;
} & {
  [key: string]: string | number | boolean;
};

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

interface AutoComplete {
  className?: string;
  label?: string;
  size: "small" | "medium";
  options?: Option[];
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

  const handleChange = (value: Option | Option[] | null) => {
    if (setSelected && Array.isArray(value)) {
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
          <li {...props}>
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
        onChange={(event, value) => {
          console.log(event)
          handleChange(value)
        }}
        value={getSelectedOptions()}
        renderTags={() => null}
      />
    </>
  );
}

// const useStyles = makeStyles({ name: { AutoComplete } })(() => ({
//   checkbox: {
//     marginRight: 8,
//   },
// }));
