import Container from "@/components/map/panels/Container";

import { Text } from "@p4b/ui/components/theme";

const FilterPanel = () => {
  return (
    <Container header={<Text typo="page heading">Filter</Text>} body={<Text typo="body 1">Body</Text>} />
  );
};

export default FilterPanel;
