"use client";

import { Box, useTheme } from "@mui/material";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useMemo, useRef } from "react";
import type { MapRef } from "react-map-gl/maplibre";
import { MapProvider } from "react-map-gl/maplibre";
import { shallowEqual, useSelector } from "react-redux";

import { usePublicProject } from "@/lib/api/projects";
import type { RootState } from "@/lib/store";
import { selectFilteredProjectLayers } from "@/lib/store/layer/selectors";
import { setProjectLayers } from "@/lib/store/layer/slice";
import { selectActiveBasemap } from "@/lib/store/map/selectors";
import { setProject } from "@/lib/store/map/slice";
import type { Project, ProjectLayer } from "@/lib/validations/project";

import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import { LoadingPage } from "@/components/common/LoadingPage";
import Header from "@/components/header/Header";
import MapViewer from "@/components/map/MapViewer";
import PublicProjectNavigation from "@/components/map/panels/PublicProjectNavigation";

export default function MapPage({ params: { projectId } }) {
  const { sharedProject, isLoading, isError: projectError } = usePublicProject(projectId);
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const activeBasemap = useAppSelector(selectActiveBasemap);
  const projectLayers = useMemo(() => {
    return sharedProject?.config?.["layers"] ?? ([] as ProjectLayer[]);
  }, [sharedProject]);
  const project = sharedProject?.config?.["project"] as Project;
  const mapRef = useRef<MapRef | null>(null);
  const initialView = sharedProject?.config?.["initial_view_state"] ?? {};

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

  return (
    <>
      {isLoading && <LoadingPage />}
      {!isLoading && !projectError && project && (
        <MapProvider>
          <Header showHambugerMenu={false} mapHeader={true} project={project} viewOnly />
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
              <PublicProjectNavigation projectLayers={_projectLayers} />
            </Box>
            <MapViewer
              layers={_projectLayers}
              mapRef={mapRef}
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
              isEditor={false}
            />
          </Box>
        </MapProvider>
      )}
    </>
  );
}
