"use client";

import { languages } from "@/app/i18/settings";
import ThemeRegistry from "@/lib/ThemeRegistry";
import AuthProvider from "@/lib/providers/AuthProvider";
import ToastProvider from "@/lib/providers/ToastProvider";
import StoreProvider from "@/lib/store/providers/StoreProvider";
import "@/styles/globals.css";
import { dir } from "i18next";
import type { Metadata } from "next";
import "react-toastify/dist/ReactToastify.css";
import { makeStyles } from "@/lib/theme";

export const metadata: Metadata = {
  title: {
    template: "%s | GOAT",
    default: "GOAT",
  },
  description: "Geo Open Accessibiliy Tool",
};

export async function generateStaticParams() {
  return languages.map((lng) => ({ lng }));
}

export default function RootLayout({
  children,
  params: { lng },
}: {
  children: React.ReactNode;
  params: { lng: string };
}) {

  const {classes} = useStyles()

  return (
    <html lang={lng} dir={dir(lng)}>
      <body className={classes.body}>
      <StoreProvider>
        <AuthProvider>
          <ToastProvider>
            <ThemeRegistry>{children}</ThemeRegistry>
          </ToastProvider>
        </AuthProvider>
      </StoreProvider>
      </body>
    </html>
  );
}

const useStyles = makeStyles({ name: { RootLayout } })((theme) => ({
  body: {
    background: theme.colors.useCases.surfaces.background,
  },
}));