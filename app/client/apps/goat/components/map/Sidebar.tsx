"use client";

import { makeStyles } from "@/lib/theme";
import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, Tooltip } from "@mui/material";
import type { CSSProperties } from "react";

import type { ICON_NAME } from "@p4b/ui/components/Icon";
import { Icon } from "@p4b/ui/components/Icon";
import { useTheme } from "@p4b/ui/components/theme";

export type MapSidebarItem = {
  icon: ICON_NAME;
  name: string;
  component?: JSX.Element;
  link?: string;
};
export type MapSidebarProps = {
  className?: string;
  topItems?: MapSidebarItem[];
  centerItems?: MapSidebarItem[];
  bottomItems?: MapSidebarItem[];
  width: number;
  position: "left" | "right";
  active?: MapSidebarItem;
  onClick?: (active: MapSidebarItem) => void;
};

export type MapSidebarListProps = {
  items: MapSidebarItem[];
  classes: Record<string, string>;
  justifyContent: CSSProperties["justifyContent"];
  sidebarPosition: MapSidebarProps["position"];
  active?: MapSidebarItem;
  onClick?: (active: MapSidebarItem) => void;
};

const MapSidebarList = (props: MapSidebarListProps) => {
  const { items, classes, justifyContent, sidebarPosition, active } = props;
  const theme = useTheme();

  const htmlColor = (name: string) => {
    if (name === active?.name) {
      return theme.colors.palette.focus.main;
    }
    return theme.isDarkModeEnabled ? "white" : theme.colors.palette.light.greyVariant4;
  };

  return (
    <List
      className={classes.list}
      sx={{
        justifyContent,
      }}>
      {items.map((item) => (
        <Tooltip
          key={`${item.icon}_tooltip`}
          title={item.name}
          arrow
          placement={sidebarPosition == "left" ? "right" : "left"}>
          <ListItem key={item.icon} disablePadding disableGutters className={classes.listItem}>
            <ListItemButton
              className={classes.listButton}
              onClick={() => {
                if (props.onClick) {
                  props.onClick(item);
                }
              }}>
              <ListItemIcon className={classes.listItemIcon}>
                <Icon iconName={item.icon} htmlColor={htmlColor(item.name)} fontSize="small" />
              </ListItemIcon>
            </ListItemButton>
          </ListItem>
        </Tooltip>
      ))}
    </List>
  );
};

export default function MapSidebar(props: MapSidebarProps) {
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
          active={props.active}
          classes={classes}
          justifyContent="flex-start"
          sidebarPosition={props.position}
          onClick={props.onClick}
        />
        <MapSidebarList
          items={props.centerItems ?? []}
          active={props.active}
          classes={classes}
          justifyContent="center"
          sidebarPosition={props.position}
          onClick={props.onClick}
        />
        <MapSidebarList
          items={props.bottomItems ?? []}
          active={props.active}
          classes={classes}
          justifyContent="flex-end"
          sidebarPosition={props.position}
          onClick={props.onClick}
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
      padding: 0,
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
      minHeight: 60,
      justifyContent: "center",
      "&:hover": {
        backgroundColor: theme.colors.useCases.surfaces.surface2,
      },
    },
  })
);
