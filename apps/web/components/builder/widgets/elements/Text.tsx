import { Box } from "@mui/material";

import type { TextElementSchema } from "@/lib/validations/widget";

const TextElementWidget = ({ config }: { config: TextElementSchema }) => {
  return (
    config.setup.text && (
      <Box>
        <div dangerouslySetInnerHTML={{ __html: config.setup.text }} />
      </Box>
    )
  );
};

export default TextElementWidget;
