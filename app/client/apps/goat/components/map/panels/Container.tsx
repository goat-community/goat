import { makeStyles } from "@/lib/theme";
import { Divider, Stack } from "@mui/material";
import React from "react";

interface ContainerProps {
  header?: React.ReactNode;
  body?: React.ReactNode;
  action?: React.ReactNode;
}

export default function Container({ header, body, action }: ContainerProps) {
  const { classes } = useStyles();
  return (
    <Stack className={classes.root}>
      {header && (
        <Stack className={classes.header} direction="row" justifyContent="space-between" alignItems="center">
          {header}
        </Stack>
      )}
      <Divider />
      {body && (
        <Stack direction="column" className={classes.body}>
          {body}
        </Stack>
      )}
      {action && (
        <Stack direction="row" className={classes.action}>
          {action}
        </Stack>
      )}
    </Stack>
  );
}

const useStyles = makeStyles({ name: { Container } })((theme) => ({
  root: {
    backgroundColor: theme.colors.useCases.surfaces.surface1,
    height: "100%",
  },
  header: {
    marginBottom: theme.spacing(2),
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3),
  },
  body: {
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(7),
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3),
    overflowY: "auto",
    scrollbarGutter: "stable both-edges",
    "&::-webkit-scrollbar": {
      width: "6px",
    },
    "&::-webkit-scrollbar-thumb": {
      background: "#2836484D",
      borderRadius: "3px",
      "&:hover": {
        background: "#28364880",
      },
    },
  },
  action: {
    position: "fixed",
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3),
    bottom: 0,
    backgroundColor: theme.colors.useCases.surfaces.surface1,
  },
}));
