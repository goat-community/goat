import { makeStyles } from "@/lib/theme";
import { Box, Divider, Stack } from "@mui/material";

interface ContainerProps {
  header?: React.ReactNode;
  body?: React.ReactNode;
  action?: React.ReactNode;
}

export default function Container({ header, body, action }: ContainerProps) {
  const { classes, cx } = useStyles();
  return (
    <Stack className={classes.root}>
      {header && (
        <Stack className={classes.header} direction="row" justifyContent="space-between">
          {header}
        </Stack>
      )}
      <Divider></Divider>
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
    padding: theme.spacing(3),
    height: "100%",
  },
  header: {
    marginBottom: theme.spacing(2),
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(2),
  },
  body: {
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  action: {
    position: "absolute",
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
    bottom: 0,
  },
}));
