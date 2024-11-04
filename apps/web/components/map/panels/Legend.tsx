import { useMemo } from "react";

import { useTranslation } from "@/i18n/client";

import { setActiveLeftPanel } from "@/lib/store/map/slice";

import { useFilteredProjectLayers, useLayerActions } from "@/hooks/map/LayerPanelHooks";
import { useAppDispatch } from "@/hooks/store/ContextHooks";

import { Legend, LegendMapContainer } from "@/components/map/controls/Legend";
import Container from "@/components/map/panels/Container";

interface PanelProps {
  projectId: string;
  isFloating?: boolean;
  showAllLayers?: boolean;
}

const LegendPanel = ({ projectId, isFloating = false, showAllLayers = false }: PanelProps) => {
  const { t } = useTranslation("common");
  const dispatch = useAppDispatch();
  const { layers: projectLayers, mutate: mutateProjectLayers } = useFilteredProjectLayers(projectId);
  const { toggleLayerVisibility } = useLayerActions(projectLayers);
  const _layers = useMemo(
    () =>
      showAllLayers
        ? projectLayers
        : projectLayers?.filter((layer) => {
            return layer.properties?.visibility;
          }),
    [projectLayers, showAllLayers]
  );
  return (
    <>
      {!isFloating && (
        <Container
          title={t("legend")}
          close={() => dispatch(setActiveLeftPanel(undefined))}
          direction="left"
          body={projectLayers && <Legend layers={_layers} hideZoomLevel />}
        />
      )}
      {isFloating && (
        <LegendMapContainer
          layers={_layers}
          enableActions={showAllLayers}
          hideZoomLevel
          onVisibilityChange={async (layer) => {
            const { layers: _layers, layerToUpdate: _layerToUpdate } = toggleLayerVisibility(layer);
            await mutateProjectLayers(_layers, false);
          }}
        />
      )}
    </>
  );
};

export default LegendPanel;
