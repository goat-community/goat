"use client";

import { makeStyles } from "@/lib/theme";
import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, Tooltip } from "@mui/material";
import { CSSProperties } from "react";

import { FaIcon, ICON_NAME } from "@p4b/ui/components/DataDisplay/FAIcon";
import { useTheme } from "@p4b/ui/components/theme";

export type MapSidebarItem = {
  icon: ICON_NAME;
  name: string;
};
export type MapSidebarProps = {
  className?: string;
  topItems?: MapSidebarItem[];
  centerItems?: MapSidebarItem[];
  bottomItems?: MapSidebarItem[];
  width: number;
  position: "left" | "right";
};

export type MapSidebarListProps = {
  items: MapSidebarItem[];
  classes: Record<string, string>;
  justifyContent: CSSProperties["justifyContent"];
  sidebarPosition: MapSidebarProps["position"];
};

const MapSidebarList = (props: MapSidebarListProps) => {
  const { items, classes, justifyContent, sidebarPosition } = props;
  const theme = useTheme();
  return (
    <List
      className={classes.list}
      sx={{
        justifyContent,
      }}>
      {items.map(({ icon, name }, index) => (
        <Tooltip title={name} arrow placement={sidebarPosition == "left" ? "right" : "left"}>
          <ListItem key={icon} disablePadding disableGutters className={classes.listItem}>
            <ListItemButton className={classes.listButton}>
              <ListItemIcon className={classes.listItemIcon}>
                <FaIcon
                  iconName={icon}
                  htmlColor={theme.isDarkModeEnabled ? "white" : "gray"}
                  fontSize="small"
                />
              </ListItemIcon>
            </ListItemButton>
          </ListItem>
        </Tooltip>
      ))}
    </List>
  );
};

export default function MapSidebar(props: MapSidebarProps) {
  const theme = useTheme();
  const { classes, cx } = useStyles({ sidebarWidth: props.width });

  return (
    <Drawer
      variant="permanent"
      open={false}
      anchor={props.position}
      className={cx(classes.root, props.className)}>
      <Box className={classes.box}>
        <MapSidebarList
          items={props.topItems ?? []}
          classes={classes}
          justifyContent="flex-start"
          sidebarPosition={props.position}
        />
        <MapSidebarList
          items={props.centerItems ?? []}
          classes={classes}
          justifyContent="center"
          sidebarPosition={props.position}
        />
        <MapSidebarList
          items={props.bottomItems ?? []}
          classes={classes}
          justifyContent="flex-end"
          sidebarPosition={props.position}
        />
      </Box>
    </Drawer>
  );
}

const useStyles = makeStyles<{ sidebarWidth: number }>({ name: { MapSidebar } })(
  (theme, { sidebarWidth }) => ({
    root: {
      ".MuiDrawer-paper": {
        flexShrink: 0,
        whiteSpace: "nowrap",
        border: "none",
        width: sidebarWidth,
        overflowX: "hidden",
        overflowY: "hidden",
        boxSizing: "border-box",
      },
    },
    box: {
      display: "grid",
      height: "100%",
      gridTemplateRows: "repeat(3, 1fr)",
      justify: "center",
    },
    list: {
      display: "flex",
      width: sidebarWidth,
      flexDirection: "column",
    },
    listItem: {
      display: "block",
    },
    listItemIcon: {
      minWidth: 0,
      mr: "auto",
      justifyContent: "center",
    },
    listButton: {
      minHeight: 50,
      justifyContent: "center",
      px: 2.5,
      "&:hover": {
        backgroundColor: theme.colors.useCases.surfaces.surface2,
      },
    },
  })
);
