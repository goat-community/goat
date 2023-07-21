import { Box } from "@mui/material";
import React from "react";

interface SingleGridProps {
  children: React.ReactNode;
  span: 1 | 2 | 3 | 4;
}

const SingleGrid = (props: SingleGridProps) => {
  const { children, span } = props;

  return <Box sx={{ width: `${23.75 * span + span - 1}%` }}>{children}</Box>;
};

export default SingleGrid;
