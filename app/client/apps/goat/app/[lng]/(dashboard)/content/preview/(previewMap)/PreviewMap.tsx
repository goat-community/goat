"use client";

import { makeStyles } from "@/lib/theme";
import { TextField } from "@mui/material";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map, { ScaleControl, NavigationControl } from "react-map-gl";

import BasicAccordion from "@p4b/ui/components/BasicAccordion";

const useStyles = makeStyles({ name: { PreviewMap } })(() => ({
  root: {
    padding: "18px 0",
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    height: "732px",
  },
  mapContainer: {
    width: "100%",
    height: "100%",
    border: "1px solid var(--light-primary-shades-8-p, rgba(43, 179, 129, 0.08))",
    boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
    background: "#FAFAFA",
    padding: "16px",
  },
  menuContainer: {
    width: "280px",
    borderRadius: "4px",
    border: "1px solid rgba(43, 179, 129, 0.08)",
    boxShadow: "0px 2px 4px -1px rgba(0, 0, 0, 0.12)",
    background: "#FAFAFA",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
}));

export default function PreviewMap(props) {
  const { initial_view_state, map_style, scale_show, navigation_control, children } = props;

  const { classes, cx } = useStyles();

  return (
    <div className={cx(classes.root)}>
      <div className={cx(classes.menuContainer)}>
        <TextField id="outlined-basic" label="342423432.xml" variant="outlined" />
        <BasicAccordion title="Info">
          <div>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur, rem.</div>
        </BasicAccordion>
        <BasicAccordion title="Attributes">
          <div>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur, rem.</div>
          <div>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur, rem.</div>
          <div>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur, rem.</div>
        </BasicAccordion>
      </div>
      <div className={cx(classes.mapContainer)}>
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
    </div>
  );
}
