// Copyright (c) 2020 GitHub user u/garronej

/* eslint-disable react/display-name */
import MuiAlert from "@mui/material/Alert";
import { useReducer, memo } from "react";
import type { ReactNode } from "react";

import { makeStyles } from "../lib/ThemeProvider";
import { Text } from "./theme";

export type AlertProps = {
  className?: string;
  classes?: Partial<ReturnType<typeof useStyles>["classes"]>;
  severity: "warning" | "info" | "error" | "success";
  doDisplayCross?: boolean;
  children: NonNullable<ReactNode>;
};



export const Alert = memo((props: AlertProps) => {
  const { severity, children, className } = props;

  const { classes, cx } = useStyles({ severity }, { props });

  const [isClosed] = useReducer(() => true, false);

  if (isClosed) {
    return null;
  }

  return (
    <MuiAlert
      className={cx(classes.root, className)}
      severity={severity}
      classes={{
        action: classes.action,
        icon: classes.icon,
      }}
      action={
         undefined
      }>
      {typeof children === "string" ? (
        <Text typo="label 2" color="primary">
          {children}
        </Text>
      ) : (
        children
      )}
    </MuiAlert>
  );
});

const useStyles = makeStyles<{ severity: AlertProps["severity"] }>({
  name: { Alert },
})((theme, { severity }) => ({
  root: {
    alignItems: "center",
    color: theme.colors.useCases.typography.textPrimary,
    backgroundColor: theme.colors.useCases.alertSeverity[severity].background,
  },
  icon: {
    color: theme.colors.useCases.alertSeverity[severity].main,
  },
  action: {
    alignItems: "center",
    padding: 0,
  },
}));
