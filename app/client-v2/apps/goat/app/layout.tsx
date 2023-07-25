import ThemeRegistry from "@/lib/ThemeRegistry";
import AuthProvider from "@/lib/providers/AuthProvider";
import StoreProvider from "@/lib/providers/StoreProvider";
import ToastProvider from "@/lib/providers/ToastProvider";
import type { Metadata } from "next";
import "react-toastify/dist/ReactToastify.css";

import "../styles/globals.css";

export const metadata: Metadata = {
  title: {
    template: "%s | GOAT",
    default: "GOAT",
  },
  description: "Geo Open Accessibiliy Tool",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
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
