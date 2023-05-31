import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import InfoIcon from "@mui/icons-material/Info";
import { Link, Stack, Typography } from "@mui/material";

import { GOATLogoDarkSvg } from "../assets/svg/GOATLogoDark";
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
    <Stack className={cx(classes.root)} direction="row" justifyContent="space-between" alignItems="center">
      <GOATLogoDarkSvg width={144} height={36} />
      <Typography variant="h3">Search bar goes here</Typography>
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
    height: 52,
    top: 0,
    left: 0,
    right: 0,
    padding: theme.spacing(4),
  },
}));
