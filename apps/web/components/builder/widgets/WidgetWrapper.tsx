import { Box } from "@mui/material";

import type { BuilderWidgetSchema } from "@/lib/validations/project";
import { chartTypes } from "@/lib/validations/widget";

import WidgetChart from "@/components/builder/widgets/chart/Chart";

interface WidgetWrapper {
  widget: BuilderWidgetSchema;
}

const WidgetWrapper: React.FC<WidgetWrapper> = ({ widget }) => {
  return (
    <Box sx={{ width: "100%" }}>
      {widget.config?.type && chartTypes.options.includes(widget.config?.type) && (
        <WidgetChart config={widget.config} />
      )}
    </Box>
  );
};

export default WidgetWrapper;
