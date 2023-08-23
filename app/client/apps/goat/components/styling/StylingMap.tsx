"use client";

import "mapbox-gl/dist/mapbox-gl.css";
import maplibregl from "maplibre-gl";
import React, { useEffect, useRef } from "react";
// import { NavigationControl, ScaleControl } from "react-map-gl";
// import Map from "react-map-gl";
import { useSelector } from "react-redux";

import Box from "@p4b/ui/components/Box";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {IStore} from "@/types/store";

const StylingMap = () => {
  const { initialViewState } = useSelector((state: IStore) => state.styling);

  const { classes } = useStyles();

  const mapContainerRef = useRef(null);

  console.log("initialViewState", initialViewState);

  useEffect(() => {
    //todo change after Initialize the map
    const map = new maplibregl.Map({
      container: mapContainerRef.current ?? '',
      style: "https://api.maptiler.com/maps/topo-v2/style.json?key=169weMz7cpAoQfwWeK8n",
      center: [11.5696284, 48.1502132], // Set the center coordinates
      zoom: 12, // Set the initial zoom level
    });

    // Clean up the map when the component unmounts
    return () => map.remove();
  }, []);

  return (
    <Box ref={mapContainerRef} className={classes.root}>
      {/*<Map*/}
      {/*  initialViewState={initialViewState}*/}
      {/*  style={{ width: "100%", height: "100%" }}*/}
      {/*  mapStyle="mapbox://styles/mapbox/streets-v11"*/}
      {/*  mapboxAccessToken={process.env.NEXT_PUBLIC_MAP_TOKEN}>*/}
      {/*  <ScaleControl />*/}
      {/*  <NavigationControl />*/}
      {/*  /!*{children}*!/*/}
      {/*</Map>*/}
    </Box>
  );
};

const useStyles = makeStyles({ name: { StylingMap } })(() => ({
  root: {
    width: "100%",
    height: "100vh",
  },
}));

export default StylingMap;
