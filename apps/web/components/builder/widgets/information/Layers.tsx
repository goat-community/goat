import { Box } from "@mui/material";
import { useParams } from "next/navigation";

import { updateProjectLayer } from "@/lib/api/projects";
import { updateProjectLayer as updateLocalProjectLayer } from "@/lib/store/layer/slice";
import type { ProjectLayer } from "@/lib/validations/project";
import type { LayerInformationSchema } from "@/lib/validations/widget";

import { useFilteredProjectLayers, useLayerActions } from "@/hooks/map/LayerPanelHooks";
import { useAppDispatch } from "@/hooks/store/ContextHooks";

import { Legend } from "@/components/map/controls/Legend";

interface LayerInformationProps {
  config: LayerInformationSchema;
  projectLayers: ProjectLayer[];
  viewOnly?: boolean;
}

const LayerInformationWidget = ({
  projectLayers: publishedProjectLayers,
  viewOnly,
}: LayerInformationProps) => {
  const dispatch = useAppDispatch();
  const { projectId } = useParams() as { projectId: string };
  const { mutate: mutateProjectLayers, layers: projectLayers } = useFilteredProjectLayers(projectId);
  const { toggleLayerVisibility } = useLayerActions(projectLayers);
  return (
    <Box>
      <Legend
        layers={viewOnly ? publishedProjectLayers : projectLayers}
        enableActions
        hideZoomLevel
        onVisibilityChange={async (layer) => {
          if (viewOnly) {
            dispatch(
              updateLocalProjectLayer({
                id: layer.id,
                changes: {
                  properties: {
                    ...layer.properties,
                    visibility: !layer.properties.visibility,
                  },
                },
              })
            );
          } else {
            const { layers: _layers, layerToUpdate: _layerToUpdate } = toggleLayerVisibility(layer);
            await mutateProjectLayers(_layers, false);
            await updateProjectLayer(projectId, layer.id, _layerToUpdate);
          }
        }}
      />
    </Box>
  );
};

export default LayerInformationWidget;
