"use client";

import { Box, Theme, useMediaQuery, useTheme } from "@mui/material";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useMemo, useRef } from "react";
import type { MapRef } from "react-map-gl/maplibre";
import { MapProvider } from "react-map-gl/maplibre";
import { shallowEqual, useSelector } from "react-redux";

import { usePublicProject } from "@/lib/api/projects";
import type { RootState } from "@/lib/store";
import { selectFilteredProjectLayers } from "@/lib/store/layer/selectors";
import { setProjectLayers } from "@/lib/store/layer/slice";
import { setProject } from "@/lib/store/map/slice";
import type { Project, ProjectLayer } from "@/lib/validations/project";

import { useBasemap } from "@/hooks/map/MapHooks";
import { useAppDispatch } from "@/hooks/store/ContextHooks";

import { LoadingPage } from "@/components/common/LoadingPage";
import MapViewer from "@/components/map/MapViewer";
import PublicProjectLayout from "@/components/map/layouts/desktop/PublicProjectLayout";
import MobileProjectLayout from "@/components/map/layouts/mobile/MobileProjectLayout";

export default function MapPage({ params: { projectId } }) {
  const { sharedProject, isLoading, isError: projectError } = usePublicProject(projectId);
  console.log(sharedProject);
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { activeBasemap } = useBasemap(sharedProject?.config?.["project"] as Project);
  const projectLayers = useMemo(() => {
    return sharedProject?.config?.["layers"] ?? ([] as ProjectLayer[]);
  }, [sharedProject]);
  const project = sharedProject?.config?.["project"] as Project;
  const mapRef = useRef<MapRef | null>(null);
  const initialView = sharedProject?.config?.["project"]?.["initial_view_state"] ?? {};

  const _projectLayers = useSelector(
    (state: RootState) => selectFilteredProjectLayers(state, ["table"]),
    shallowEqual
  );

  useEffect(() => {
    if (projectLayers && project) {
      dispatch(setProjectLayers(projectLayers));
      dispatch(setProject(project));
    }
  }, [dispatch, project, projectLayers]);
  const isMobile = useMediaQuery((theme: Theme) => theme.breakpoints.down("md"));
  return (
    <>
      {isLoading && <LoadingPage />}
      {!isLoading && !projectError && project && (
        <MapProvider>
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
            <Box
              sx={{
                position: "absolute",
                width: "100%",
                height: "100%",
              }}>
              {isMobile ? (
                <MobileProjectLayout project={project} projectLayers={_projectLayers} viewOnly />
              ) : (
                <PublicProjectLayout project={project} projectLayers={_projectLayers} viewOnly />
              )}
            </Box>
            <MapViewer
              layers={_projectLayers}
              mapRef={mapRef}
              touchZoomRotate
              maxExtent={project?.max_extent || undefined}
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
              isEditor={false}
            />
          </Box>
        </MapProvider>
      )}
    </>
  );
}
