"use client";

import { makeStyles } from "@/lib/theme";
import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";

import BasicAccordion from "@p4b/ui/components/BasicAccordion";
import { TextField } from "@p4b/ui/components/Text/TextField";

const useStyles = () =>
  makeStyles({ name: { PreviewMenu } })(() => ({
    root: {
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

export default function PreviewMenu() {
  const { classes, cx } = useStyles()();

  return (
    <div className={cx(classes.root)}>
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
  );
}
