"use client";

import { Box, debounce, useTheme } from "@mui/material";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import type { MapRef, ViewStateChangeEvent } from "react-map-gl/maplibre";
import { MapProvider } from "react-map-gl/maplibre";

import { useTranslation } from "@/i18n/client";

import { updateProjectInitialViewState, useProject, useProjectInitialViewState } from "@/lib/api/projects";
import { PATTERN_IMAGES } from "@/lib/constants/pattern-images";
import { DrawProvider } from "@/lib/providers/DrawProvider";
import { selectActiveBasemap } from "@/lib/store/map/selectors";
import { addOrUpdateMarkerImages, addPatternImages } from "@/lib/transformers/map-image";
import type { FeatureLayerPointProperties } from "@/lib/validations/layer";

import { useAuthZ } from "@/hooks/auth/AuthZ";
import { useJobStatus } from "@/hooks/jobs/JobStatus";
import { useFilteredProjectLayers } from "@/hooks/map/LayerPanelHooks";
import { useAppSelector } from "@/hooks/store/ContextHooks";

import { LoadingPage } from "@/components/common/LoadingPage";
import Header from "@/components/header/Header";
import MapViewer from "@/components/map/MapViewer";
import ProjectNavigation from "@/components/map/panels/ProjectNavigation";

const UPDATE_VIEW_STATE_DEBOUNCE_TIME = 3000;

export default function MapPage({ params: { projectId } }) {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const activeBasemap = useAppSelector(selectActiveBasemap);
  const mapRef = useRef<MapRef | null>(null);
  const {
    project,
    isLoading: isProjectLoading,
    isError: projectError,
    mutate: mutateProject,
  } = useProject(projectId);

  const {
    initialView,
    isLoading: isInitialViewLoading,
    isError: projectInitialViewError,
  } = useProjectInitialViewState(projectId);

  const {
    isLoading: areProjectLayersLoading,
    isError: projectLayersError,
    layers: projectLayers,
    mutate: mutateProjectLayers,
  } = useFilteredProjectLayers(projectId, ["table"], []);

  const { isProjectEditor, isLoading: isAuthZLoading } = useAuthZ();

  const isLoading = useMemo(
    () => isProjectLoading || isInitialViewLoading || areProjectLayersLoading || isAuthZLoading,
    [isProjectLoading, isInitialViewLoading, areProjectLayersLoading, isAuthZLoading]
  );

  const hasError = useMemo(
    () => projectError || projectInitialViewError || projectLayersError,
    [projectError, projectInitialViewError, projectLayersError]
  );

  const updateViewState = useMemo(
    () =>
      debounce((e: ViewStateChangeEvent) => {
        updateProjectInitialViewState(projectId, {
          zoom: e.viewState.zoom,
          latitude: e.viewState.latitude,
          longitude: e.viewState.longitude,
          pitch: e.viewState.pitch,
          bearing: e.viewState.bearing,
          min_zoom: initialView?.min_zoom ?? 0,
          max_zoom: initialView?.max_zoom ?? 24,
        });
      }, UPDATE_VIEW_STATE_DEBOUNCE_TIME),
    [initialView?.max_zoom, initialView?.min_zoom, projectId]
  );

  const handleMapLoad = useCallback(() => {
    if (mapRef.current) {
      // get all icon layers and add icons to map using addOrUpdateMarkerImages method
      projectLayers?.forEach((layer) => {
        if (layer.type === "feature" && layer.feature_layer_geometry_type === "point") {
          const pointFeatureProperties = layer.properties as FeatureLayerPointProperties;
          addOrUpdateMarkerImages(layer.id, pointFeatureProperties, mapRef.current);
        }
      });

      // load pattern images
      addPatternImages(PATTERN_IMAGES ?? [], mapRef.current);
    }
  }, [projectLayers]);

  useEffect(() => {
    // icons are added to the style, so if the basestyle changes we have to reload icons to the style
    // it takes forever for certain styles to load so we have to wait a bit.
    // Couldn't find an event that catches the basemap change
    const debouncedHandleMapLoad = debounce(handleMapLoad, 200);
    debouncedHandleMapLoad();
  }, [activeBasemap.url, handleMapLoad]);

  useJobStatus(() => {
    mutateProjectLayers();
    mutateProject();
  });

  return (
    <>
      {isLoading && <LoadingPage />}
      {!isLoading && !hasError && (
        <MapProvider>
          <DrawProvider>
            <Header
              title={`${t("project")} ${project?.name ?? ""}`}
              showHambugerMenu={false}
              tags={project?.tags}
              lastSaved={project?.updated_at}
            />
            <Box
              sx={{
                display: "flex",
                height: "100vh",
                width: "100%",
                [theme.breakpoints.down("sm")]: {
                  marginLeft: "0",
                  width: `100%`,
                },
              }}>
              <Box>
                <ProjectNavigation projectId={projectId} />
              </Box>
              <MapViewer
                layers={projectLayers}
                mapRef={mapRef}
                initialViewState={{
                  zoom: initialView?.zoom ?? 3,
                  latitude: initialView?.latitude ?? 48.13,
                  longitude: initialView?.longitude ?? 11.57,
                  pitch: initialView?.pitch ?? 0,
                  bearing: initialView?.bearing ?? 0,
                  fitBoundsOptions: {
                    minZoom: initialView?.min_zoom ?? 0,
                    maxZoom: initialView?.max_zoom ?? 24,
                  },
                }}
                mapStyle={activeBasemap?.url}
                {...(isProjectEditor ? { onMoveEnd: updateViewState } : {})}
                isEditor={isProjectEditor}
              />
            </Box>
          </DrawProvider>
        </MapProvider>
      )}
    </>
  );
}
