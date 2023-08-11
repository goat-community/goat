import Container from "@/components/map/panels/Container";
import { Button, Typography } from "@mui/material";

import { Text } from "@p4b/ui/components/theme";

const LayerPanel = () => {
  return (
    <Container
      header={<Text typo="page heading" color="focus" >Layers</Text>}
      body={<Typography variant="body1">Body</Typography>}
    />
  );
};

export default LayerPanel;
