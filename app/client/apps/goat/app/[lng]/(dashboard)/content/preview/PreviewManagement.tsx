"use client";

import PreviewData from "@/app/[lng]/(dashboard)/content/preview/(previewData)/PreviewData";
import PreviewMap from "@/app/[lng]/(dashboard)/content/preview/(previewMap)/PreviewMap";
import HeaderStack from "@/app/[lng]/(dashboard)/content/preview/HeaderStack";
import { API } from "@/lib/api/apiConstants";
import { layerFetcher, mapDataFetcher } from "@/lib/services/dashboard";
import { makeStyles } from "@/lib/theme";
import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";
import type {IStore} from "@/types/store";

const useStyles = makeStyles({ name: { PreviewManagement } })(() => ({
  root: {
    position: "relative",
    width: "100%",
    minHeight: "100vh",
    marginTop: "100px",
  },
}));

interface PreviewManagementProps {
  id: string;
}

export default function PreviewManagement(props: PreviewManagementProps) {
  const { id } = props;
  const { previewMode } = useSelector((state: IStore) => state.content);

  const { data, error } = useSWR("map", mapDataFetcher);
  const { data: layerData, trigger: layerTrigger } = useSWRMutation(API.layer, layerFetcher);

  const { classes, cx } = useStyles();

  console.log("layerData", layerData);

  useEffect(() => {
    if (id) layerTrigger(id);
  }, [id, layerTrigger]);

  if (error) {
    return <div>Error fetching data</div>;
  }

  if (!data) {
    return <div>Loading...</div>;
  }

  const previewObj = {
    map: <PreviewMap {...data} />,
    table: <PreviewData />,
  };

  return (
    <div className={cx(classes.root)}>
      <HeaderStack />
      {previewObj[previewMode]}
    </div>
  );
}
