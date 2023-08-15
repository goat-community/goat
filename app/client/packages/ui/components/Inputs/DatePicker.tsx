import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker as MUIDatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DemoContainer } from "@mui/x-date-pickers/internals/demo";
import dayjs from "dayjs";
import type { Dayjs } from "dayjs";

interface DatePickerProps {
  onChange: (value: Dayjs | null) => void;
  value: Dayjs | null;
  label?: string;
  ClassName?: string;
  size?: "small" | "medium";
}

/**
 * A custom DatePicker component that renders a Material-UI DatePicker with additional features.
 * @param {DatePickerProps} props - The props for the DatePicker component.
 * @returns The rendered DatePicker component.
 */

export function DatePicker(props: DatePickerProps) {
  const { onChange, value = dayjs("2022-04-17"), label, ClassName, size = "medium" } = props;

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DemoContainer components={["MUIDatePicker"]}>
        <MUIDatePicker
          slotProps={{ textField: { size: size } }}
          className={ClassName}
          label={label}
          value={value}
          onChange={(newValue) => onChange(newValue)}
        />
      </DemoContainer>
    </LocalizationProvider>
  );
}
