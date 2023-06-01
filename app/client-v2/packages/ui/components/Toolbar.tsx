import { Link, Stack, Typography } from "@mui/material";

import { GOATLogoDarkSvg } from "../assets/svg/GOATLogoDark";
import { makeStyles } from "../lib/ThemeProvider";

export type ToolbarProps = {
  items: { link: string; icon: () => JSX.Element }[];
  height: number;
};

export function Toolbar(props: ToolbarProps) {
  const { items } = props;
  const { classes, cx } = useStyles(props)();

  return (
    <Stack className={cx(classes.root)} direction="row" justifyContent="space-between" alignItems="center">
      <GOATLogoDarkSvg width={144} height={36} />
      <Typography variant="h3">Search bar goes here</Typography>
      <Stack direction="row" alignItems="center" spacing={6}>
        {items?.map(({ link, icon }) => (
          <Link href={link} key={link}>
            {icon()}
          </Link>
        ))}
      </Stack>
    </Stack>
  );
}

const useStyles = (props: ToolbarProps) =>
  makeStyles({ name: { Toolbar } })((theme) => ({
    root: {
      position: "fixed",
      backgroundColor: theme.colors.useCases.surfaces.background,
      height: props.height,
      top: 0,
      left: 0,
      right: 0,
      padding: theme.spacing(4),
    },
  }));
