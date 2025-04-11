import { Box } from "@mui/material";

import type { ProjectLayer } from "@/lib/validations/project";
import type { LayerInformationSchema } from "@/lib/validations/widget";

import { Legend } from "@/components/map/controls/Legend";

interface LayerInformationProps {
  config: LayerInformationSchema;
  projectLayers: ProjectLayer[];
}

const LayerInformationWidget = ({ config, projectLayers }: LayerInformationProps) => {
  return (
    <Box>
      <Legend
        layers={projectLayers}
        enableActions
        hideZoomLevel
        onVisibilityChange={async (layer) => {
          console.log(layer);
          // Handle visibility change logic here
        }}
      />
    </Box>
  );
};

export default LayerInformationWidget;
