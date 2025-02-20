"use client";

import { DndContext } from "@dnd-kit/core";
import { Box, Stack, debounce, useTheme } from "@mui/material";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import type { MapRef, ViewStateChangeEvent } from "react-map-gl/maplibre";
import { MapProvider } from "react-map-gl/maplibre";
import { toast } from "react-toastify";

import { useTranslation } from "@/i18n/client";

import {
  updateProject,
  updateProjectInitialViewState,
  useProject,
  useProjectInitialViewState,
  useProjectScenarioFeatures,
} from "@/lib/api/projects";
import { PATTERN_IMAGES } from "@/lib/constants/pattern-images";
import { DrawProvider } from "@/lib/providers/DrawProvider";
import { addOrUpdateMarkerImages, addPatternImages } from "@/lib/transformers/map-image";
import type { FeatureLayerPointProperties } from "@/lib/validations/layer";

import { useAuthZ } from "@/hooks/auth/AuthZ";
import { useJobStatus } from "@/hooks/jobs/JobStatus";
import { useFilteredProjectLayers } from "@/hooks/map/LayerPanelHooks";
import { useBasemap } from "@/hooks/map/MapHooks";
import { useAppSelector } from "@/hooks/store/ContextHooks";

import BuilderConfigPanel from "@/components/builder/ConfigPanel";
import { LoadingPage } from "@/components/common/LoadingPage";
import Header from "@/components/header/Header";
import MapViewer from "@/components/map/MapViewer";
import ProjectNavigation from "@/components/map/panels/ProjectNavigation";
import PublicProjectLayout from "@/components/map/panels/PublicProjectLayout";

const UPDATE_VIEW_STATE_DEBOUNCE_TIME = 200;

export default function MapPage({ params: { projectId } }) {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const mapRef = useRef<MapRef | null>(null);
  const mapMode = useAppSelector((state) => state.map.mapMode);
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

  const { activeBasemap } = useBasemap(project);

  const { isProjectEditor, isLoading: isAuthZLoading } = useAuthZ();

  const { scenarioFeatures } = useProjectScenarioFeatures(projectId, project?.active_scenario_id);
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleProjectUpdate = async (key: string, value: any, refresh = false) => {
    try {
      const projectToUpdate = JSON.parse(JSON.stringify(project));
      projectToUpdate[key] = value;
      mutateProject(projectToUpdate, refresh);
      await updateProject(projectId, { [key]: value });
    } catch (error) {
      toast.error(t("error_updating_project"));
      mutateProject();
    }
  };

  console.log(initialView);

  return (
    <>
      {isLoading && <LoadingPage />}
      {!isLoading && !hasError && project && (
        <MapProvider>
          <DrawProvider>
            <Stack component="div" width="100%" height="100%" overflow="hidden">
              <Header
                showHambugerMenu={false}
                mapHeader={true}
                project={project}
                onProjectUpdate={handleProjectUpdate}
              />
              <Box
                sx={{
                  display: "flex",
                  height: "100%",
                  width: "100%",
                  [theme.breakpoints.down("sm")]: {
                    marginLeft: "0",
                    width: `100%`,
                  },
                }}>
                <DndContext>
                  {mapMode === "data" && <ProjectNavigation project={project} />}
                  <Box
                    sx={{
                      padding: mapMode === "builder" ? "20px" : "0",
                      width: "100%",
                      height: "100%",
                      position: "relative",
                    }}>
                    {mapMode === "builder" && (
                      <Box
                        sx={{
                          position: "absolute",
                          inset: "20px",
                        }}>
                        <PublicProjectLayout
                          projectLayers={projectLayers}
                          project={project}
                          onProjectUpdate={handleProjectUpdate}
                        />
                      </Box>
                    )}
                    <MapViewer
                      layers={projectLayers}
                      mapRef={mapRef}
                      scenarioFeatures={scenarioFeatures}
                      maxExtent={project?.max_extent}
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
                  {mapMode === "builder" && (
                    <BuilderConfigPanel project={project} onProjectUpdate={handleProjectUpdate} />
                  )}
                </DndContext>
              </Box>
            </Stack>
          </DrawProvider>
        </MapProvider>
      )}
    </>
  );
}
