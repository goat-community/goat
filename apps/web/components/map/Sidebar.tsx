"use client";

import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, Tooltip, useTheme } from "@mui/material";
import type { CSSProperties } from "react";

import { Icon } from "@p4b/ui/components/Icon";

import type { MapSidebarItemID } from "@/types/map/common";
import type { MapSidebarItem } from "@/types/map/sidebar";

export type MapSidebarProps = {
  className?: string;
  topItems?: MapSidebarItem[];
  centerItems?: MapSidebarItem[];
  bottomItems?: MapSidebarItem[];
  width: number;
  position: "left" | "right";
  active?: MapSidebarItemID;
  onClick?: (active: MapSidebarItem) => void;
};

const MapSidebarList = (props: MapSidebarListProps) => {
  const { items, justifyContent, sidebarPosition, active, sidebarWidth } = props;
  const theme = useTheme();

  return (
    <List
      dense
      sx={{
        justifyContent,
        display: "flex",
        width: sidebarWidth,
        flexDirection: "column",
        padding: 0,
      }}>
      {items.map((item) => (
        <Tooltip
          key={`${item.icon}_tooltip`}
          title={item.name}
          arrow
          placement={sidebarPosition == "left" ? "right" : "left"}>
          <ListItem
            key={item.icon}
            disablePadding
            sx={{
              display: "block",
            }}>
            <ListItemButton
              disabled={item.disabled ?? false}
              selected={item.id === active && !item.disabled}
              sx={{
                minHeight: sidebarWidth,
              }}
              onClick={() => {
                if (props.onClick) {
                  props.onClick(item);
                }
              }}>
              <ListItemIcon sx={{ minWidth: 0, mr: "auto", justifyContent: "center" }}>
                <Icon
                  iconName={item.icon}
                  htmlColor={item.id === active && !item.disabled ? theme.palette.primary.main : "inherit"}
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

export type MapSidebarListProps = {
  items: MapSidebarItem[];
  justifyContent: CSSProperties["justifyContent"];
  sidebarPosition: MapSidebarProps["position"];
  active?: MapSidebarItemID;
  sidebarWidth: number;
  onClick?: (active: MapSidebarItem) => void;
};

export default function MapSidebar(props: MapSidebarProps) {
  const { width } = props;

  return (
    <Drawer
      variant="permanent"
      open={false}
      anchor={props.position}
      sx={{
        ".MuiDrawer-paper": {
          flexShrink: 0,
          whiteSpace: "nowrap",
          border: "none",
          width: width,
          overflowX: "hidden",
          overflowY: "hidden",
          boxSizing: "border-box",
        },
      }}>
      <Box
        sx={{
          display: "grid",
          height: "100%",
          gridTemplateRows: "repeat(3, 1fr)",
          justify: "center",
        }}>
        <MapSidebarList
          items={props.topItems ?? []}
          active={props.active}
          sidebarWidth={width}
          justifyContent="flex-start"
          sidebarPosition={props.position}
          onClick={props.onClick}
        />
        <MapSidebarList
          items={props.centerItems ?? []}
          active={props.active}
          sidebarWidth={width}
          justifyContent="center"
          sidebarPosition={props.position}
          onClick={props.onClick}
        />
        <MapSidebarList
          items={props.bottomItems ?? []}
          active={props.active}
          sidebarWidth={width}
          justifyContent="flex-end"
          sidebarPosition={props.position}
          onClick={props.onClick}
        />
      </Box>
    </Drawer>
  );
}
