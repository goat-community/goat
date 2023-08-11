"use client";

import MapSidebar, { MapSidebarItem, MapSidebarProps } from "@/components/map/Sidebar";
import { MapToolbar, MapToolbarProps } from "@/components/map/Toolbar";
import Charts from "@/components/map/panels/Charts";
import Layer from "@/components/map/panels/Layer";
import Legend from "@/components/map/panels/Legend";
import { MAPBOX_TOKEN } from "@/lib/constants";
import { makeStyles } from "@/lib/theme";
import { Box, Divider } from "@mui/material";
import "mapbox-gl/dist/mapbox-gl.css";
import React, { useState } from "react";
import Map from "react-map-gl";
import { CSSObject } from "tss-react";

import { ICON_NAME } from "@p4b/ui/components/DataDisplay/FAIcon";

export default function MapPage() {
  const sidebarWidth = 48;
  const toolbarHeight = 52;
  const { classes, cx } = useStyles({ sidebarWidth, toolbarHeight });

  const toolbar: MapToolbarProps = {
    projectTitle: "@project_title",
    lastSaved: "08:35am 03/07/2023",
    tags: ["Bike Sharing Project", "City of Hamburg"],
    height: toolbarHeight,
  };

  const [activeLeft, setActiveLeft] = useState<MapSidebarItem | undefined>(undefined);
  const [activeRight, setActiveRight] = useState<MapSidebarItem | undefined>(undefined);
  const leftSidebar: MapSidebarProps = {
    topItems: [
      {
        icon: ICON_NAME.LAYERS,
        name: "Layers",
        component: <Layer />,
      },
      {
        icon: ICON_NAME.LEGEND,
        name: "Legend",
        component: <Legend />,
      },
      {
        icon: ICON_NAME.CHART,
        name: "Charts",
        component: <Charts />,
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
      <Box>
        <MapToolbar {...toolbar} />
        <MapSidebar
          {...leftSidebar}
          className={classes.sidebar}
          active={activeLeft}
          onClick={(item) => setActiveLeft(item.name === activeLeft?.name ? undefined : item)}
        />

        {activeLeft?.component && (
          <Box className={cx(classes.panel, classes.leftPanel)}>
            {activeLeft.component}
          </Box>
        )}
        {activeRight?.component && (
          <Box className={cx(classes.panel, classes.rightPanel)}>{activeRight.component}</Box>
        )}
        <MapSidebar
          {...rightSidebar}
          className={classes.sidebar}
          active={activeRight}
          onClick={(item) => setActiveRight(item.name === activeRight?.name ? undefined : item)}
        />
      </Box>
      <div className={cx(classes.root)}>
        <Map
          style={{ width: "100%", height: "100%" }}
          initialViewState={{
            longitude: -122.4,
            latitude: 37.8,
            zoom: 14,
          }}
          mapStyle="mapbox://styles/mapbox/streets-v9"
          mapboxAccessToken={MAPBOX_TOKEN}></Map>
      </div>
    </div>
  );
}

const useStyles = makeStyles<{ sidebarWidth: number; toolbarHeight: number }>({
  name: { MapPage },
})((theme, { sidebarWidth, toolbarHeight }, classes) => {
  const offsetHeight: CSSObject = {
    height: `calc(100% - ${toolbarHeight}px)`,
    marginTop: toolbarHeight,
  };
  const offsetWidth: CSSObject = {
    width: `calc(100% - ${sidebarWidth}px)`,
    marginLeft: sidebarWidth,
  };
  return {
    container: {
      display: "flex",
      height: "100vh",
      ...offsetWidth,
    },
    root: {
      ...offsetHeight,
      width: "100%",
    },
    sidebar: {
      ".MuiDrawer-paper": {
        ...offsetHeight,
      },
    },
    panel: {
      ...offsetHeight,
    },
    leftPanel: {
      width: 300,
      borderLeft: `2px solid ${theme.colors.palette.light.greyVariant1}`,
    },
    rightPanel: {
      width: 300,
    },
  };
});
