import Container from "@/components/map/panels/Container";
import { Button, Typography } from "@mui/material";

const ChartsPanel = () => {
  return (
    <Container
      header={<Typography variant="h6">Header</Typography>}
      body={<Typography variant="body1">Charts</Typography>}
      action={<Button variant="contained">Action</Button>}
    />
  );
};

export default ChartsPanel;
