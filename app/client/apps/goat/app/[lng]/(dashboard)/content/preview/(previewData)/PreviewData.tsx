"use client";

import { makeStyles } from "@/lib/theme";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";

const useStyles = makeStyles({ name: { PreviewData } })(() => ({
  root: {
    display: "flex",
  },
}));

export default function PreviewData() {
  const { classes, cx } = useStyles();

  return <div className={cx(classes.root)}>Preview data</div>;
}
