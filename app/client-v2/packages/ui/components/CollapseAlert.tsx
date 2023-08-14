import CloseIcon from "@mui/icons-material/Close";
import { Alert, AlertTitle } from "@mui/lab";
import { Collapse, IconButton } from "@mui/material";
import * as React from "react";

export type CollapseAlertProps = {
  open: boolean;
  setOpen: (boolean) => void;
  title: string;
  description: string;
  severity: "success" | "info" | "warning" | "error";
};

export const CollapseAlert = (props: CollapseAlertProps) => {
  const { title, description, setOpen, open, severity } = props;
  return (
    <Collapse in={open}>
      <Alert
        severity={severity}
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={() => {
              setOpen(false);
            }}>
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }>
        <AlertTitle>{title}</AlertTitle>
        {description}
      </Alert>
    </Collapse>
  );
};
