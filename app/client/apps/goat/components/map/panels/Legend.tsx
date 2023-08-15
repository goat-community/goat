import Container from "@/components/map/panels/Container";
import { Button } from "@mui/material";

import { Text } from "@p4b/ui/components/theme";

const LegendPanel = () => {
  return (
    <Container
      header={<Text typo="page heading">Legend</Text>}
      body={<Text typo="body 1">Body</Text>}
      action={<Button variant="contained">Action</Button>}
    />
  );
};

export default LegendPanel;
