"use client";

import { makeStyles } from "@/lib/theme";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map, { ScaleControl, NavigationControl } from "react-map-gl";

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

export default function PreviewMap(props: any) {
  const { initial_view_state, MAP_ACCESS_TOKEN, map_style, scale_show, navigation_control } = props;

  const { classes, cx } = useStyles();

  return (
    <div className={cx(classes.root)}>
      <Map
        initialViewState={initial_view_state}
        style={{ width: "100%", height: "100%" }}
        mapStyle={map_style}
        mapboxAccessToken={MAP_ACCESS_TOKEN}>
        {scale_show && <ScaleControl />}
        {navigation_control && <NavigationControl />}
      </Map>
    </div>
  );
}
