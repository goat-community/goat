"use client";

import { ToastContainer, Zoom } from "react-toastify";

interface ToastProviderProps {
  children: React.ReactNode;
}

export default function ToastProvider({ children }: ToastProviderProps) {
  return (
    <>
      {children}
      <ToastContainer transition={Zoom} position="top-center" autoClose={2000} />
    </>
  );
}
