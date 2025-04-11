import { Box, Typography } from "@mui/material";

import type { ProjectLayer } from "@/lib/validations/project";
import type { WidgetInformationConfig } from "@/lib/validations/widget";
import { informationTypes } from "@/lib/validations/widget";

import LayerWidget from "@/components/builder/widgets/information/Layers";

interface WidgetInformationProps {
  config: WidgetInformationConfig;
  projectLayers: ProjectLayer[];
}

const WidgetInformation: React.FC<WidgetInformationProps> = ({ config, projectLayers }) => {
  return (
    <Box sx={{ minHeight: 200 }}>
      {config.setup?.title && (
        <Typography variant="body1" fontWeight="bold" align="left" gutterBottom>
          {config.setup?.title}
        </Typography>
      )}
      {config.type === informationTypes.Values.layers && (
        <LayerWidget config={config} projectLayers={projectLayers} />
      )}
    </Box>
  );
};

export default WidgetInformation;
