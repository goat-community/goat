import { Box, useTheme } from "@mui/material";

import { Loading } from "@p4b/ui/components/Loading";

export function LoadingPage() {
  const theme = useTheme();
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        width: "100vw",
        backgroundColor: theme.palette.background.default,
      }}>
      <Loading />
    </Box>
  );
}
