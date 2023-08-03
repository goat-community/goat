import { languages } from "@/app/i18/settings";
import ThemeRegistry from "@/lib/ThemeRegistry";
import AuthProvider from "@/lib/providers/AuthProvider";
import StoreProvider from "@/lib/providers/StoreProvider";
import ToastProvider from "@/lib/providers/ToastProvider";
import "@/styles/globals.css";
import { dir } from "i18next";
import type { Metadata } from "next";
import "react-toastify/dist/ReactToastify.css";

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

export default function RootLayout({ children, params: { lng } }) {
  return (
    <html lang={lng} dir={dir(lng)}>
      <body style={{ backgroundColor: "#f2f2f3" }}>
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
