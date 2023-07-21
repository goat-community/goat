import Radio from "@mui/material/Radio";
import * as React from "react";

interface RadioProps {
  value: string;
  onCheck?: (value: string) => void;
  selectedValue?: string;
}

/**
 * A radio input component that allows users to select a single option from a group.
 * @param {RadioProps} props - The props for the radio input component.
 * @returns The rendered radio input component.
 */

export function RadioInput(props: RadioProps) {
  const { value, onCheck, selectedValue } = props;

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onCheck) {
      onCheck(event.target.value);
    }
  };

  return (
    <div>
      <Radio
        checked={selectedValue === value}
        onChange={handleChange}
        value={value}
        name="radio-buttons"
        inputProps={{ "aria-label": value }}
      />
    </div>
  );
}
