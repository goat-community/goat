import { Box } from "@mui/material";

import type { WidgetElementConfig } from "@/lib/validations/widget";

import DividerElementWidget from "@/components/builder/widgets/elements/Divider";
import ImageElementWidget from "@/components/builder/widgets/elements/Image";
import TextElementWidget from "@/components/builder/widgets/elements/Text";

interface WidgetElementProps {
  config: WidgetElementConfig;
}

const WidgetElement: React.FC<WidgetElementProps> = ({ config }) => {
  return (
    <Box sx={{ width: "100%" }}>
      {config.type === "text" && <TextElementWidget config={config} />}
      {config.type === "divider" && <DividerElementWidget config={config} />}
      {config.type === "image" && <ImageElementWidget config={config} />}
    </Box>
  );
};

export default WidgetElement;
