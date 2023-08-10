"use client";

import { makeStyles } from "@/lib/theme";
import { AppBar, Box, Stack, Toolbar } from "@mui/material";

import { GOATLogoIconOnlyGreen } from "@p4b/ui/assets/svg/GOATLogoIconOnlyGreen";

export type MapToolbarProps = {
  items: { link: string; icon: () => JSX.Element }[];
  height: number;
};

export function MapToolbar(props: MapToolbarProps) {
  const { items } = props;
  const { classes, cx } = useStyles(props)();

  return (
    <AppBar className={cx(classes.root)} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar variant='dense' sx={{ minHeight: props.height, height: props.height }}>
        <GOATLogoIconOnlyGreen className={classes.logo} />
        <Box sx={{ flexGrow: 1 }} />
        <Stack direction="row" alignItems="center">
          {items?.map(({ link, icon }, index) => icon())}
        </Stack>
      </Toolbar>
    </AppBar>
  );
}

const useStyles = (props: MapToolbarProps) =>
  makeStyles({ name: { MapToolbar } })((theme) => ({
    root: {
      position: "fixed",
      backgroundColor: theme.colors.useCases.surfaces.background,
      height: props.height,
      boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)"
    },
    logo: {
      width: "30px",
      height: "30px",
      cursor: "pointer"
    },
    icon: {
      borderRight: `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].light}14`,
      padding: "4px",
      paddingRight: theme.spacing(3),
      marginRight: theme.spacing(3),
    },
  }));
