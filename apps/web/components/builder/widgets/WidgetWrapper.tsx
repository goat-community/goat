/* eslint-disable @typescript-eslint/no-explicit-any */
import { Box } from "@mui/material";

import type { BuilderWidgetSchema, ProjectLayer } from "@/lib/validations/project";
import type {
  WidgetChartConfig,
  WidgetElementConfig,
  WidgetInformationConfig,
} from "@/lib/validations/widget";
import { chartTypes, elementTypes, informationTypes } from "@/lib/validations/widget";

import WidgetChart from "@/components/builder/widgets/chart/WidgetChart";
import WidgetElement from "@/components/builder/widgets/elements/WidgetElement";
import WidgetInformation from "@/components/builder/widgets/information/WidgetInformation";

interface WidgetWrapper {
  widget: BuilderWidgetSchema;
  projectLayers: ProjectLayer[];
}

const WidgetWrapper: React.FC<WidgetWrapper> = ({ widget, projectLayers }) => {
  return (
    <Box sx={{ width: "100%", p: 2, pointerEvents: "all" }}>
      {widget.config?.type && chartTypes.options.includes(widget.config?.type as any) && (
        <WidgetChart config={widget.config as WidgetChartConfig} />
      )}
      {widget.config?.type && elementTypes.options.includes(widget.config?.type as any) && (
        <WidgetElement config={widget.config as WidgetElementConfig} />
      )}
      {widget.config?.type && informationTypes.options.includes(widget.config?.type as any) && (
        <WidgetInformation config={widget.config as WidgetInformationConfig} projectLayers={projectLayers} />
      )}
    </Box>
  );
};

export default WidgetWrapper;
