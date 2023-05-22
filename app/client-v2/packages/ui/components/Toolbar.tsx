import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import InfoIcon from "@mui/icons-material/Info";
import { Link, Stack, Typography } from "@mui/material";

import { TOOLBAR_HEIGHT } from "../constants/toolbar";
import { makeStyles } from "../lib/ThemeProvider";
import { createIcon } from "./Icon";

const { Icon } = createIcon({
  info: InfoIcon,
  profile: AccountCircleIcon,
});

export type ToolbarProps = {
  items: { link: string; iconId: "info" | "profile" }[];
};

export function Toolbar(props: ToolbarProps) {
  const { items } = props;
  const { classes, cx } = useStyles();

  return (
    <Stack
      className={cx(classes.root)}
      direction="row"
      justifyContent="space-between"
      alignItems="center"
      padding="21.5px">
      <Typography color="white" variant="h1">
        GOAT
      </Typography>
      <Typography color="white" variant="h3">
        Search bar goes here
      </Typography>
      <Stack direction="row" alignItems="center" spacing="32px">
        {items?.map(({ link, iconId }) => (
          <Link href={link} key={iconId}>
            <Icon iconId={iconId} />
          </Link>
        ))}
      </Stack>
    </Stack>
  );
}

const useStyles = makeStyles({ name: { Toolbar } })((theme) => ({
  root: {
    position: "fixed",
    backgroundColor: theme.colors.palette.dark.light,
    height: TOOLBAR_HEIGHT,
    top: 0,
    left: 0,
    right: 0,
  },
}));