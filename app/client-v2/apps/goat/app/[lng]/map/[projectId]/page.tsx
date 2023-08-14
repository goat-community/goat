"use client";

import MapSidebar, { MapSidebarItem, MapSidebarProps } from "@/components/map/Sidebar";
import { MapToolbar, MapToolbarProps } from "@/components/map/Toolbar";
import { BasemapSelector } from "@/components/map/controls/BasemapSelector";
// import Attribution from "@/components/map/controls/Attribution";
import Charts from "@/components/map/panels/Charts";
import Filter from "@/components/map/panels/Filter";
import Layer from "@/components/map/panels/Layer";
import Legend from "@/components/map/panels/Legend";
import MapStyle from "@/components/map/panels/MapStyle";
import Scenario from "@/components/map/panels/Scenario";
import Toolbox from "@/components/map/panels/Toolbox";
import { MAPBOX_TOKEN } from "@/lib/constants";
import { makeStyles } from "@/lib/theme";
import { Box, Collapse, Stack } from "@mui/material";
import "mapbox-gl/dist/mapbox-gl.css";
import React, { useEffect, useRef, useState } from "react";
import Map, { MapProvider } from "react-map-gl";
import { CSSObject } from "tss-react";

import { ICON_NAME } from "@p4b/ui/components/DataDisplay/FAIcon";

export default function MapPage() {
  const sidebarWidth = 48;
  const toolbarHeight = 52;
  const { classes, cx } = useStyles({ sidebarWidth, toolbarHeight });

  const toolbar: MapToolbarProps = {
    projectTitle: "@project_title",
    lastSaved: "08:35am 03/07/2023",
    tags: ["Bike Sharing Project", "City of Munich"],
    height: toolbarHeight,
  };

  const [activeLeft, setActiveLeft] = useState<MapSidebarItem | undefined>(undefined);
  const prevActiveLeftRef = useRef<MapSidebarItem | undefined>(undefined);
  useEffect(() => {
    prevActiveLeftRef.current = activeLeft;
  }, [activeLeft]);

  const [activeRight, setActiveRight] = useState<MapSidebarItem | undefined>(undefined);
  const prevActiveRightRef = useRef<MapSidebarItem | undefined>(undefined);
  useEffect(() => {
    prevActiveRightRef.current = activeRight;
  }, [activeRight]);
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
    ],
    bottomItems: [
      {
        icon: ICON_NAME.HELP,
        name: "Help",
        link: "https://docs.plan4better.de",
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
        component: <Toolbox />,
      },
      {
        icon: ICON_NAME.FILTER,
        name: "Filter",
        component: <Filter />,
      },
      {
        icon: ICON_NAME.SCENARIO,
        name: "Scenario",
        component: <Scenario />,
      },
      {
        icon: ICON_NAME.STYLE,
        name: "Map Style",
        component: <MapStyle />,
      },
    ],
    width: sidebarWidth,
    position: "right",
  };

  const basemaps = [
    {
      value: "mapbox_streets",
      url: "mapbox://styles/mapbox/streets-v12",
      title: "High Fidelity",
      subtitle: "Great for public presentations",
      thumbnail: "https://i.imgur.com/aVDMUKAm.png",
    },
    {
      value: "mapbox_satellite",
      url: "mapbox://styles/mapbox/satellite-streets-v12",
      title: "Satellite Streets",
      subtitle: "As seen from space",
      thumbnail: "https://i.imgur.com/JoMGuUOm.png",
    },
    {
      value: "mapbox_light",
      url: "mapbox://styles/mapbox/light-v11",
      title: "Light",
      subtitle: "For highlitghting data overlays",
      thumbnail: "https://i.imgur.com/jHFGEEQm.png",
    },
    {
      value: "mapbox_dark",
      url: "mapbox://styles/mapbox/dark-v11",
      title: "Dark",
      subtitle: "For highlighting data overlays",
      thumbnail: "https://i.imgur.com/PaYV5Gjm.png",
    },
    {
      value: "mapbox_navigation",
      url: "mapbox://styles/mapbox/navigation-day-v1",
      title: "Traffic",
      subtitle: "Live traffic data",
      thumbnail: "https://i.imgur.com/lfcARxZm.png",
    },
  ];
  const [activeBasemapIndex, setActiveBasemapIndex] = useState([0]);

  return (
    <MapProvider>
      <div className={cx(classes.container)}>
        <Box>
          <MapToolbar {...toolbar} />
          <MapSidebar
            {...leftSidebar}
            className={classes.sidebar}
            active={activeLeft}
            onClick={(item) => {
              if (item.link) {
                window.open(item.link, "_blank");
                return;
              } else {
                setActiveLeft(item.name === activeLeft?.name ? undefined : item);
              }
            }}
          />

          <Stack direction="row" className={cx(classes.collapse, classes.collapseLeft)}>
            <Collapse
              timeout={200}
              orientation="horizontal"
              in={activeLeft !== undefined}
              sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
              onExited={() => {
                setActiveLeft(undefined);
                prevActiveLeftRef.current = undefined;
              }}>
              {(activeLeft?.component !== undefined ||
                prevActiveLeftRef.current?.component !== undefined) && (
                <Box className={cx(classes.controls, classes.leftPanel)}>
                  {activeLeft?.component || prevActiveLeftRef.current?.component}
                </Box>
              )}
            </Collapse>
            {/* Left Controls */}
          </Stack>
          <Stack
            direction="row"
            className={cx(classes.collapse, classes.collapseRight)}
            sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Stack
              direction="column"
              justifyContent="space-between"
              className={cx(classes.controls, classes.mapControls)}>
              <Stack direction="column">
                {/* <Box sx={{ height: 152, width: 52, bgcolor: "primary.main" }} /> */}
              </Stack>
              <Stack direction="column">
                {/* <Attribution showMapboxLogo={true} showOsmBasemapAttribution={true} datasetAttributions={[]} /> */}
                <BasemapSelector
                  styles={basemaps}
                  active={activeBasemapIndex}
                  basemapChange={(basemap) => {
                    setActiveBasemapIndex(basemap);
                  }}
                />
              </Stack>
            </Stack>
            <Collapse
              timeout={200}
              orientation="horizontal"
              in={activeRight !== undefined}
              onExit={() => {
                setActiveRight(undefined);
                prevActiveRightRef.current = undefined;
              }}>
              {(activeRight?.component !== undefined ||
                prevActiveRightRef.current?.component !== undefined) && (
                <Box className={cx(classes.controls, classes.rightPanel)}>
                  {activeRight?.component || prevActiveRightRef.current?.component}
                </Box>
              )}
            </Collapse>
          </Stack>
          <MapSidebar
            {...rightSidebar}
            className={classes.sidebar}
            active={activeRight}
            onClick={(item) => {
              if (item.link) {
                window.open(item.link, "_blank");
                return;
              } else {
                setActiveRight(item.name === activeRight?.name ? undefined : item);
              }
            }}
          />
        </Box>
        <div className={cx(classes.root)}>
          <Map
            style={{ width: "100%", height: "100%" }}
            initialViewState={{
              longitude: 11.575936741828286,
              latitude: 48.13780235991851,
              zoom: 12,
            }}
            mapStyle={basemaps[activeBasemapIndex[0]].url}
            attributionControl={false}
            mapboxAccessToken={MAPBOX_TOKEN}></Map>
        </div>
      </div>
    </MapProvider>
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
    width: `calc(100% - ${2 * sidebarWidth}px)`,
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
      ".mapboxgl-ctrl .mapboxgl-ctrl-logo": {
        display: "none",
      },
    },
    sidebar: {
      ".MuiDrawer-paper": {
        ...offsetHeight,
      },
    },
    controls: {
      ...offsetHeight,
    },
    mapControls: {
      padding: theme.spacing(4),
    },
    leftPanel: {
      width: 300,
      borderLeft: `2px solid ${theme.colors.palette.light.greyVariant1}`,
    },
    rightPanel: {
      width: 300,
      borderRight: `2px solid ${theme.colors.palette.light.greyVariant1}`,
    },
    collapse: {
      height: "100%",
      position: "absolute",
      top: 0,
    },
    collapseLeft: {
      left: sidebarWidth,
    },
    collapseRight: {
      right: sidebarWidth,
    },
  };
});
