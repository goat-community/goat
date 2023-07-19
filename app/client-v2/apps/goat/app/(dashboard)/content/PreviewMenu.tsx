import ContentPage from "@/app/(dashboard)/content/page";
import { makeStyles } from "@/lib/theme";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";

const useStyles = () =>
  makeStyles({ name: { ContentPage } })(() => ({
    root: {
      width: "280px",
    },
  }));

export default function PreviewMenu() {
  const { classes, cx } = useStyles()();

  return <div className={cx(classes.root)}>Menu</div>;
}
