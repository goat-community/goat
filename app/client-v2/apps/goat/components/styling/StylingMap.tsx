"use client";

import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import { NavigationControl, ScaleControl } from "react-map-gl";
import Map from "react-map-gl";
import { useSelector } from "react-redux";

import Box from "@p4b/ui/components/Box";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

const StylingMap = () => {
  const { initialViewState } = useSelector((state) => state.styling);

  const { classes } = useStyles();

  console.log("initialViewState", initialViewState);

  return (
    <Box className={classes.root}>
      <Map
        initialViewState={initialViewState}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/streets-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAP_TOKEN}>
        <ScaleControl />
        <NavigationControl />
        {/*{children}*/}
      </Map>
    </Box>
  );
};

const useStyles = makeStyles({ name: { StylingMap } })((theme) => ({
  root: {
    width: "100%",
    height: "100vh",
  },
}));

export default StylingMap;
