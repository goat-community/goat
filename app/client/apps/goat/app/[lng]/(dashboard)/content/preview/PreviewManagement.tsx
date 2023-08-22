"use client";

import HeaderStack from "@/app/[lng]/(dashboard)/content/preview/HeaderStack";
import PreviewMap from "@/app/[lng]/(dashboard)/content/preview/PreviewMap";
import PreviewMenu from "@/app/[lng]/(dashboard)/content/preview/PreviewMenu";
import { API } from "@/lib/api/apiConstants";
import { layerFetcher } from "@/lib/services/dashboard";
import { makeStyles } from "@/lib/theme";
import mapData from "@/lib/utils/project_layers_demo_update";
import React, { useEffect } from "react";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

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

interface PreviewManagementProps {
  id: string;
}

// Function to simulate fetching data asynchronously
const mapDataFetcher = () => {
  return new Promise((resolve, reject) => {
    // Simulate an asynchronous delay (e.g., 1 second)
    setTimeout(() => {
      resolve(mapData);
    }, 1000); // Simulate a 1-second delay
  });
};

export default function PreviewManagement(props: PreviewManagementProps) {
  const { id } = props;

  const { data, error } = useSWR("map", mapDataFetcher);
  const { data: layerData, trigger: layerTrigger } = useSWRMutation(API.layer, layerFetcher);

  const { classes, cx } = useStyles();

  useEffect(() => {
    if (id) layerTrigger(id);
  }, [id, layerTrigger]);

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
