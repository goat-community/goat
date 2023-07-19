"use client";

import CssBaseline from "@mui/material/CssBaseline";
import React from "react";
import { NextAppDirEmotionCacheProvider } from "tss-react/next/appDir";

import { ThemeProvider } from "./theme";

const ThemeRegistry = ({ children }: React.PropsWithChildren) => {
  return (
    <>
      <CssBaseline />
      <NextAppDirEmotionCacheProvider options={{ key: "mui" }}>
        <ThemeProvider>{children}</ThemeProvider>
      </NextAppDirEmotionCacheProvider>
    </>
  );
};

export default ThemeRegistry;
