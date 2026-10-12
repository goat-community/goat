import dayjs from "dayjs";
import "dayjs/locale/de";
import "dayjs/locale/en-gb";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DesktopTimePicker } from "@mui/x-date-pickers/DesktopTimePicker";
import { useTheme } from "@mui/material";

import type { TemporalLocale } from "./temporalFormats";

type TimePickerProps = {
  time: number; // time in seconds
  onChange: (time: number) => void;
  errorMessage?: string;
  error?: boolean;
  /** Locale to display in: both read the time as 24h (`07:00`), where the
   * adapter's default English locale shows `07:00 AM`. */
  locale?: TemporalLocale;
};

export default function TimePicker(props: TimePickerProps) {
  const theme = useTheme();
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale={props.locale ?? "en-gb"}>
      <DesktopTimePicker
        slotProps={{
          actionBar: { actions: [] },
          textField: {
            error: props.error || !!props.errorMessage,
            helperText: props.errorMessage,
          },
        }}
        sx={{
          "& .MuiInputBase-root": {
            height: "40px",
            fontWeight: theme.typography.fontWeightBold,
            fontSize: theme.typography.body2.fontSize,
            color: theme.palette.text.secondary,
          },
        }}
        onChange={(newTime) => {
          const secondsFromMidnight = dayjs(newTime).diff(
            dayjs().startOf("day"),
            "second",
          );
          props.onChange(secondsFromMidnight);
        }}
        value={dayjs().startOf("day").add(props.time, "second")}
      />
    </LocalizationProvider>
  );
}
