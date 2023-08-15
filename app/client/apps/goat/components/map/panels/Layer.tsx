import Container from "@/components/map/panels/Container";

import { Text } from "@p4b/ui/components/theme";

const LayerPanel = () => {
  return (
    <Container header={<Text typo="page heading">Layers</Text>} body={<Text typo="body 1">Body</Text>} />
  );
};

export default LayerPanel;
