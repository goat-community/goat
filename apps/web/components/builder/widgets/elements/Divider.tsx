import { Box, Divider } from "@mui/material";

import type { DividerElementSchema } from "@/lib/validations/widget";

const DividerElementWidget = ({ config }: { config: DividerElementSchema }) => {
  return (
    <Box>
      <Divider />
    </Box>
  );
};

export default DividerElementWidget;
