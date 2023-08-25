"use client";

import UserInfoMenu from "@/components/UserInfoMenu";
import { makeStyles } from "@/lib/theme";
import { AppBar, Box, Chip, Stack, Toolbar } from "@mui/material";
import Divider from "@mui/material/Divider";

import { GOATLogoIconOnlyGreen } from "@p4b/ui/assets/svg/GOATLogoIconOnlyGreen";
import { Text } from "@p4b/ui/components/theme";

export type MapToolbarProps = {
  projectTitle: string;
  lastSaved: string;
  tags: string[];
  height?: number;
};

export function MapToolbar(props: MapToolbarProps) {
  const { classes, cx } = useStyles(props)();
  const { tags, projectTitle, lastSaved } = props;

  return (
    <AppBar className={cx(classes.root)} sx={{ zIndex: (theme) => theme.zIndex.drawer + 2 }}>
      <Toolbar variant="dense" sx={{ minHeight: props.height, height: props.height }}>
        <GOATLogoIconOnlyGreen className={classes.logo} />
        <Stack direction="row" alignItems="center" className={classes.infoStack}>
          <Text typo="section heading" className={classes.infoItem}>
            {projectTitle}
          </Text>
          <Divider orientation="vertical" flexItem className={classes.infoItem} />
          <Text typo="body 2" color="secondary" className={cx(classes.infoItem, classes.lastSaved)}>
            Last saved: {lastSaved}
          </Text>
          {tags &&
            tags.map((tag) => <Chip variant="outlined" label={tag} key={tag} className={classes.infoItem} />)}
        </Stack>
        <Box sx={{ flexGrow: 1 }} />
        <UserInfoMenu />
      </Toolbar>
    </AppBar>
  );
}

const useStyles = (props: MapToolbarProps) =>
  makeStyles({ name: { MapToolbar } })((theme) => ({
    root: {
      position: "fixed",
      backgroundColor: theme.colors.useCases.surfaces.surface1,
      height: props.height,
      boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
    },
    logo: {
      width: "30px",
      height: "30px",
      cursor: "pointer",
    },
    infoStack: {
      marginLeft: theme.spacing(4),
      marginRight: theme.spacing(4),
    },
    lastSaved: {
      fontStyle: "italic",
    },
    infoItem: {
      marginLeft: theme.spacing(2),
      marginRight: theme.spacing(2),
    },
    icon: {
      borderRight: `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].light}14`,
      padding: "4px",
      paddingRight: theme.spacing(4),
      marginRight: theme.spacing(4),
    },
  }));
