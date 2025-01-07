import { Stack, useTheme } from "@mui/material";
import React, { useMemo } from "react";

import { useTranslation } from "@/i18n/client";

import { MAPBOX_TOKEN } from "@/lib/constants";
import { updateProjectLayer } from "@/lib/store/layer/slice";
import { setActiveBasemap } from "@/lib/store/map/slice";
import type { ProjectLayer } from "@/lib/validations/project";

import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import { BasemapSelector } from "@/components/map/controls/BasemapSelector";
import { Fullscren } from "@/components/map/controls/Fullscreen";
import Geocoder from "@/components/map/controls/Geocoder";
import { Zoom } from "@/components/map/controls/Zoom";
import Legend from "@/components/map/panels/Legend";

const toolbarHeight = 52;

interface ProjectNavigationProps {
  projectLayers?: ProjectLayer[];
}

const PublicProjectNavigation = ({ projectLayers = [] }: ProjectNavigationProps) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation("common");
  const dispatch = useAppDispatch();
  const basemaps = useAppSelector((state) => state.map.basemaps);
  const activeBasemap = useAppSelector((state) => state.map.activeBasemap);

  const translatedBaseMaps = useMemo(() => {
    return basemaps.map((basemap) => ({
      ...basemap,
      title: i18n.exists(`common:basemap_types.${basemap.value}.title`)
        ? t(`basemap_types.${basemap.value}.title`)
        : t(basemap.title),
      subtitle: i18n.exists(`common:basemap_types.${basemap.value}.subtitle`)
        ? t(`basemap_types.${basemap.value}.subtitle`)
        : t(basemap.subtitle),
    }));
  }, [basemaps, i18n, t]);

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
              active={activeBasemap}
              basemapChange={(basemap) => {
                dispatch(setActiveBasemap(basemap));
              }}
            />
          </Stack>
        </Stack>
      </Stack>
    </>
  );
};

export default PublicProjectNavigation;
