import Container from "@/components/map/panels/Container";
import FilterManagement from "./FilterManagement";
import { Text } from "@p4b/ui/components/theme";

const FilterPanel = () => {
  return <Container header={<Text typo="page heading">Filter</Text>} body={<FilterManagement />} />;
};

export default FilterPanel;
