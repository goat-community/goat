import { Box } from "@mui/material";
import React from "react";

interface GridContainerProps {
  children: React.ReactNode;
}

const GridContainer = (props: GridContainerProps) => {
  const { children } = props;

  return <Box sx={{ marginRight: "6%", marginLeft: "13%", display: "flex", gap: "1%" }}>{children}</Box>;
};

export default GridContainer;
