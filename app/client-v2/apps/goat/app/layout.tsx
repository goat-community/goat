import ThemeRegistry from "@/lib/ThemeRegistry";
import AuthProvider from "@/lib/context/AuthProvider";
import Provider from "@/lib/context/StoreProvider";
import type { Metadata } from "next";

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
        <Provider>
          <AuthProvider>
            <ThemeRegistry>{children}</ThemeRegistry>
          </AuthProvider>
        </Provider>
      </body>
    </html>
  );
}
