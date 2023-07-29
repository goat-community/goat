import { Skeleton, Box } from "@mui/material";
import React from "react";

const SubscriptionCardSkeleton = () => {
  return (
    <Box sx={{ width: "100%", marginBottom: "32px" }}>
      <Skeleton variant="rounded" width="100%" height={210} />
    </Box>
  );
};

export default SubscriptionCardSkeleton;
