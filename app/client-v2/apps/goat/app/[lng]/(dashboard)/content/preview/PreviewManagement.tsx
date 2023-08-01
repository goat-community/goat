"use client";

import HeaderStack from "@/app/[lng]/(dashboard)/content/preview/HeaderStack";
import PreviewMap from "@/app/[lng]/(dashboard)/content/preview/PreviewMap";
import PreviewMenu from "@/app/[lng]/(dashboard)/content/preview/PreviewMenu";
import { makeStyles } from "@/lib/theme";
import mapData from "@/lib/utils/project_layers_demo_update";
import React from "react";
import useSWR from "swr";

const useStyles = makeStyles({ name: { PreviewManagement } })(() => ({
  root: {
    position: "relative",
    width: "100%",
    minHeight: "100vh",
    marginTop: "100px",
  },
  container: {
    padding: "18px 0",
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    height: "732px",
  },
}));

// Function to simulate fetching data asynchronously
const mapDataFetcher = () => {
  return new Promise((resolve, reject) => {
    // Simulate an asynchronous delay (e.g., 1 second)
    setTimeout(() => {
      resolve(mapData);
    }, 1000); // Simulate a 1-second delay
  });
};

export default function PreviewManagement() {
  const { data, error } = useSWR("map", mapDataFetcher);

  const { classes, cx } = useStyles();

  if (error) {
    return <div>Error fetching data</div>;
  }

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div className={cx(classes.root)}>
      <HeaderStack className={cx(classes.header)} />
      <div className={cx(classes.container)}>
        <PreviewMenu />
        <PreviewMap {...data} />
      </div>
    </div>
  );
}
