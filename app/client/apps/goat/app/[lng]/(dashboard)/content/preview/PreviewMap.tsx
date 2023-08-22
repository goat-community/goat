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
  const { initial_view_state, map_style, scale_show, navigation_control, children } = props;

  const { classes, cx } = useStyles();

  return (
    <div className={cx(classes.root)}>
      <Map
        initialViewState={initial_view_state}
        style={{ width: "100%", height: "100%" }}
        mapStyle={map_style || "mapbox://styles/mapbox/streets-v11"}
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAP_TOKEN}>
        {scale_show && <ScaleControl />}
        {navigation_control && <NavigationControl />}
        {children}
      </Map>
    </div>
  );
}
