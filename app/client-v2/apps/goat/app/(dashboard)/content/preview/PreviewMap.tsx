"use client";

import { makeStyles } from "@/lib/theme";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map, { ScaleControl, NavigationControl } from "react-map-gl";

export type PreviewMapType = {
  MAP_ACCESS_TOKEN: string;
  initialViewState: {
    altitude: number;
    bearing: number;
    latitude: number;
    zoom: number;
    pitch: number;
    longitude: number;
  };
  mapStyle: string;
  scaleShow: boolean;
  navigationControl: boolean;
};

const useStyles = makeStyles({ name: { PreviewMap } })(() => ({
  root: {
    width: "100%",
    height: "100%",
    border: "1px solid var(--light-primary-shades-8-p, rgba(43, 179, 129, 0.08))",
    boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
    background: "#FAFAFA",
    padding: "16px",
  },
}));

export default function PreviewMap(props: PreviewMapType) {
  const { initialViewState, MAP_ACCESS_TOKEN, mapStyle, scaleShow, navigationControl } = props;

  const { classes, cx } = useStyles();

  return (
    <div className={cx(classes.root)}>
      <Map
        initialViewState={initialViewState}
        style={{ width: "100%", height: "100%" }}
        mapStyle={mapStyle}
        mapboxAccessToken={MAP_ACCESS_TOKEN}>
        {scaleShow && <ScaleControl />}
        {navigationControl && <NavigationControl />}
      </Map>
    </div>
  );
}
