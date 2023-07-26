import type { AlertProps } from "@mui/material/Alert";
import MuiAlert from "@mui/material/Alert";
import type { AlertColor } from "@mui/material/Alert/Alert";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import * as React from "react";

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export type BasicSnackbarTypes = {
  message: string;
  severity: AlertColor;
  hideDuration?: number;
  open: boolean;
  anchorOrigin: {
    horizontal: "center" | "left" | "right";
    vertical: "bottom" | "top";
  };
};

export default function BasicSnackbar(props: BasicSnackbarTypes) {
  const { message, severity, hideDuration = 3000, open, anchorOrigin } = props;

  return (
    <Stack spacing={2} sx={{ width: "100%", padding: "20px" }}>
      <Snackbar anchorOrigin={anchorOrigin} open={open} autoHideDuration={hideDuration}>
        <Alert severity={severity} sx={{ width: "100%" }}>
          {message}
        </Alert>
      </Snackbar>
    </Stack>
  );
}
