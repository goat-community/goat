"use client";

import { Box, Skeleton } from "@mui/material";
import dynamic from "next/dynamic";

// The form reads its draft from localStorage while rendering, so it must not be server-rendered (hydration mismatch).
const NewTicketForm = dynamic(() => import("@/components/support/NewTicketForm"), {
  ssr: false,
  loading: () => (
    <Box
      sx={{
        width: "100%",
        maxWidth: 960,
        mx: "auto",
        boxSizing: "border-box",
        p: { xs: "16px 14px", md: "40px" },
      }}>
      <Skeleton variant="text" width={80} sx={{ fontSize: 14 }} />
      <Skeleton variant="text" width={260} sx={{ fontSize: 24, mt: 2 }} />
      <Skeleton variant="text" width={320} sx={{ fontSize: 14, mb: 6 }} />
      <Skeleton variant="rounded" height={520} sx={{ borderRadius: "12px" }} />
    </Box>
  ),
});

const NewTicketFormClient = () => <NewTicketForm />;

export default NewTicketFormClient;
