import { Stack, useTheme } from "@mui/material";
import React from "react";

import { useTranslation } from "@/i18n/client";

import { MAPBOX_TOKEN } from "@/lib/constants";
import { updateProjectLayer } from "@/lib/store/layer/slice";
import type { Project, ProjectLayer } from "@/lib/validations/project";

import { useBasemap } from "@/hooks/map/MapHooks";
import { useAppDispatch } from "@/hooks/store/ContextHooks";

import { BasemapSelector } from "@/components/map/controls/BasemapSelector";
import { Fullscren } from "@/components/map/controls/Fullscreen";
import Geocoder from "@/components/map/controls/Geocoder";
import { Zoom } from "@/components/map/controls/Zoom";
import Legend from "@/components/map/panels/Legend";

const toolbarHeight = 52;

interface ProjectNavigationProps {
  project: Project;
  projectLayers?: ProjectLayer[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onProjectUpdate?: (key: string, value: any, refresh?: boolean) => void;
}

const PublicProjectNavigation = ({ projectLayers = [], project }: ProjectNavigationProps) => {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const dispatch = useAppDispatch();

  const { translatedBaseMaps, activeBasemap, setActiveBasemap } = useBasemap(project);

  return (
    <>
      <Stack
        direction="row"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          height: "100%",
          position: "absolute",
          top: 0,
          pointerEvents: "all",
          [theme.breakpoints.down("sm")]: {
            left: "0",
          },
        }}>
        {/* Left Controls */}
        <Stack
          direction="column"
          sx={{
            height: `calc(100% - ${toolbarHeight}px)`,
            justifyContent: "space-between",
            marginTop: `${toolbarHeight}px`,
            padding: theme.spacing(4),
          }}>
          <Stack direction="column" sx={{ pointerEvents: "all" }}>
            <Geocoder accessToken={MAPBOX_TOKEN} placeholder={t("enter_an_address")} tooltip={t("search")} />
          </Stack>
          <Stack direction="column" sx={{ pointerEvents: "all" }}>
            <Legend
              isFloating
              showAllLayers
              projectLayers={projectLayers}
              onVisibilityChange={(layer) => {
                dispatch(
                  updateProjectLayer({
                    id: layer.id,
                    changes: {
                      properties: {
                        ...layer.properties,
                        visibility: !layer.properties.visibility,
                      },
                    },
                  })
                );
              }}
            />
          </Stack>
        </Stack>
      </Stack>
      <Stack
        direction="row"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          height: "100%",
          position: "absolute",
          top: 0,
          pointerEvents: "none",
          right: 0,
          [theme.breakpoints.down("sm")]: {
            right: "0",
          },
        }}>
        <Stack
          direction="column"
          sx={{
            height: `calc(100% - ${toolbarHeight}px)`,
            justifyContent: "space-between",
            marginTop: `${toolbarHeight}px`,
            padding: theme.spacing(4),
          }}>
          <Stack direction="column" sx={{ pointerEvents: "all" }}>
            <Zoom tooltipZoomIn={t("zoom_in")} tooltipZoomOut={t("zoom_out")} />
            <Fullscren tooltipOpen={t("fullscreen")} tooltipExit={t("exit_fullscreen")} />
          </Stack>
          <Stack direction="column" sx={{ pointerEvents: "all" }}>
            <BasemapSelector
              styles={translatedBaseMaps}
              active={activeBasemap?.value}
              basemapChange={(basemap) => {
                setActiveBasemap(basemap);
              }}
            />
          </Stack>
        </Stack>
      </Stack>
    </>
  );
};

export default PublicProjectNavigation;
