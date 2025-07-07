import { Box } from "@mui/material";

import type { ImageElementSchema } from "@/lib/validations/widget";

const ImageElementWidget = ({ config }: { config: ImageElementSchema }) => {
  return (
    <Box sx={{ height: "fit-content", maxHeight: "fit-content", width: "100%" }}>
      <img
        style={{ width: "100%", height: "auto" }}
        src={config.setup.url || "https://assets.plan4better.de/img/image-placeholder.webp"}
        alt={config.setup.alt}
      />
    </Box>
  );
};

export default ImageElementWidget;
