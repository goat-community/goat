"use client"

import { Stack, Typography } from "@mui/material"

export const Home = () => (
  <Stack sx={{ minHeight: "100vh", padding: "64px" }}>
    <Stack sx={{ flexGrow: 1, justifyContent: "center", alignItems: "center" }} component="main">
      <Typography variant="h5">main content</Typography>
    </Stack>
    <Stack direction="row" sx={{ justifyContent: "space-between" }} component="footer">
      <Typography>footer</Typography>
      <Typography>stuff</Typography>
    </Stack>
  </Stack>
)
