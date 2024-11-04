"use client";

import { useTheme } from "@mui/material";
import { ToastContainer, Zoom } from "react-toastify";

interface ToastProviderProps {
  children: React.ReactNode;
}

export default function ToastProvider({ children }: ToastProviderProps) {
  const theme = useTheme();
  return (
    <>
      {children}
      <ToastContainer transition={Zoom} position="top-center" hideProgressBar theme={theme.palette.mode} />
    </>
  );
}
