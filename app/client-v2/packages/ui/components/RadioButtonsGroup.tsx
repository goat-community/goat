import * as React from 'react';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import Box from "@mui/material/Box";

interface RadioButtonsGroupProps {
  radioLabels: object[];
  value: string;
  setValue: (value: string) => void;
  formLabel?: string | undefined;
}

export default function RadioButtonsGroup(props: RadioButtonsGroupProps) {

  const { radioLabels, value, setValue, formLabel } = props

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue((event.target as HTMLInputElement).value);
  };

  return (
    <FormControl>
      {formLabel ? <FormLabel id="demo-controlled-radio-buttons-group">formLabel</FormLabel> : null}
      <RadioGroup
        name="controlled-radio-buttons-group"
        value={value}
        onChange={handleChange}
        sx={{flexDirection: 'row', flexWrap: 'inherit'}}
      >
        {radioLabels?.map(label => (
          <Box>
            <FormControlLabel value={label.value} control={<Radio />} label={label.value} />
            {label.desc ? <Box>{label.desc}</Box> : null }
          </Box>
        ))}
      </RadioGroup>
    </FormControl>
  );
}
