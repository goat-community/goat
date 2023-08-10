"use client";

import MapSidebar, { MapSidebarProps } from "@/components/map/Sidebar";
import { MAPBOX_TOKEN } from "@/lib/constants";
import { makeStyles } from "@/lib/theme";
import { Box } from "@mui/material";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map from "react-map-gl";

import { ICON_NAME } from "@p4b/ui/components/DataDisplay/FAIcon";
import { Icon } from "@p4b/ui/components/theme";
import { MapToolbar } from "@/components/map/Toolbar";

export default function MapPage() {
  const sidebarWidth = 48;
  const toolbarHeight = 52;
  const { classes, cx } = useStyles({ sidebarWidth, toolbarHeight });

  const toolbarItems = [
    {
      link: "https://google.com",
      icon: () => (
        <div style={{ padding: "3px 10px" }}>
          <Icon iconId="help" size="medium" iconVariant="gray2" />
        </div>
      ),
    },
  ];

  const leftSidebar: MapSidebarProps = {
    topItems: [
      {
        icon: ICON_NAME.LAYERS,
        name: "Layers",
      },
      {
        icon: ICON_NAME.LEGEND,
        name: "Legend",
      },
      {
        icon: ICON_NAME.CHART,
        name: "Charts",
      },
      {
        icon: ICON_NAME.REPORT,
        name: "Reports",
      },
    ],
    bottomItems: [
      {
        icon: ICON_NAME.HELP,
        name: "Help",
      },
    ],
    width: sidebarWidth,
    position: "left",
  };

  const rightSidebar: MapSidebarProps = {
    topItems: [
      {
        icon: ICON_NAME.TOOLBOX,
        name: "Tools",
      },
      {
        icon: ICON_NAME.FILTER,
        name: "Filter",
      },
      {
        icon: ICON_NAME.SCENARIO,
        name: "Scenario",
      },
      {
        icon: ICON_NAME.STYLE,
        name: "Map Style",
      },
    ],
    width: sidebarWidth,
    position: "right",
  };

  return (
    <div className={cx(classes.container)}>
      <MapToolbar height={toolbarHeight} items={toolbarItems} />
      <div className={cx(classes.root)}>
        <Map
          style={{ width: "100%", height: "100%" }}
          initialViewState={{
            longitude: -122.4,
            latitude: 37.8,
            zoom: 14,
          }}
          mapStyle="mapbox://styles/mapbox/streets-v9"
          mapboxAccessToken={MAPBOX_TOKEN}>
          <Box sx={{ display: "flex" }}>
            <MapSidebar {...leftSidebar} className={classes.sidebar} />
            <MapSidebar {...rightSidebar} className={classes.sidebar} />
          </Box>
        </Map>
      </div>
    </div>
  );
}

const useStyles = makeStyles<{ sidebarWidth: number; toolbarHeight: number }>({ name: { MapPage } })(
  (theme, { sidebarWidth, toolbarHeight }) => ({
    container: {
      display: "flex",
      height: "100vh",
      width: `calc(100% - ${2 * sidebarWidth}px)`,
      marginLeft: sidebarWidth,
    },
    root: {
      width: "100%",
      height: `calc(100% - ${toolbarHeight}px)`,
      marginTop: toolbarHeight,
    },
    sidebar: {
      ".MuiDrawer-paper": {
        height: `calc(100% - ${toolbarHeight}px)`,
        marginTop: toolbarHeight,
      },
    },
  })
);
