import { OutlinedInput } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Radio from "@mui/material/Radio";
import Select from "@mui/material/Select";
import { useState } from "react";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 236,
    },
  },
};

type Option = {
  value: string;
  label: string;
};

type MultipleSelectProps = {
  options: Option[];
  label: string;
  defaultValue?: string[];
};

export const MultipleSelect = (props: MultipleSelectProps) => {
  const { options, label, defaultValue = [] } = props;
  const [selectedOptions, setSelectedOptions] = useState<string[]>(defaultValue);
  const handleSelectChange = (selected: string[]) => {
    setSelectedOptions(selected);
  };
  return (
    <div>
      <FormControl sx={{ m: 1, width: "100%" }}>
        <InputLabel id="demo-multiple-checkbox-label">{label}</InputLabel>
        <Select
          labelId="demo-multiple-checkbox-label"
          id="demo-multiple-checkbox"
          multiple
          value={selectedOptions}
          onChange={(e) => handleSelectChange(e.target.value as string[])}
          input={<OutlinedInput label={label} />}
          renderValue={(selected) => (selected as string[]).join(", ")}
          MenuProps={MenuProps}>
          {options.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              <Radio checked={selectedOptions.includes(option.value)} />
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
};
