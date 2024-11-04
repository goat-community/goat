import type { SxProps } from "@mui/material";
import { Slider, Stack, useTheme } from "@mui/material";

import InputTextField from "@/components/map/panels/style/other/InputTextField";

const SliderInput = ({
  value,
  isRange,
  onChange,
  onChangeCommitted,
  min = 0,
  max = 100,
  step = 1,
  rootSx,
}: {
  value: number | number[];
  isRange: boolean;
  onChange?: (newValue: number | number[]) => void;
  onChangeCommitted?: (newValue: number | number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  rootSx?: SxProps;
}) => {
  const theme = useTheme();
  return (
    <Stack
      sx={{
        ...rootSx,
      }}
      direction={isRange ? "column" : "row"}
      spacing={4}
      alignItems="center">
      <Slider
        size="small"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(_event: Event, newValue: number | number[]) => {
          onChange && onChange(newValue);
        }}
        onChangeCommitted={(_event: Event, value: number | number[]) => {
          onChangeCommitted && onChangeCommitted(value);
        }}
      />
      {!isRange && (
        <Stack>
          <InputTextField
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={(event) => {
              onChange && onChange(Number(event.target.value));
            }}
            onBlur={() => {
              onChangeCommitted && onChangeCommitted(value);
            }}
          />
        </Stack>
      )}
      {isRange && (
        <Stack
          direction="row"
          justifyContent="space-between"
          width="100%"
          style={{ marginTop: theme.spacing(1) }}>
          <InputTextField
            value={value[0]}
            onChange={(event) => {
              onChange && onChange([Number(event.target.value), value[1]]);
            }}
            onBlur={() => {
              onChangeCommitted && onChangeCommitted(value);
            }}
          />
          <InputTextField
            value={value[1]}
            onChange={(event) => {
              onChange && onChange([value[0], Number(event.target.value)]);
            }}
            onBlur={() => {
              onChangeCommitted && onChangeCommitted(value);
            }}
          />
        </Stack>
      )}
    </Stack>
  );
};
export default SliderInput;
