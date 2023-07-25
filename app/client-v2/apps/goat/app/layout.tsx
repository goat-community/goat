import ThemeRegistry from "@/lib/ThemeRegistry";
import AuthProvider from "@/lib/context/AuthProvider";
import Provider from "@/lib/context/StoreProvider";
import "@/styles/globals.css";
import type { Metadata } from "next";

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
            <ThemeRegistry>
              <div style={{ marginTop: "101px" }}>{children}</div>
            </ThemeRegistry>
          </AuthProvider>
        </Provider>
      </body>
    </html>
  );
}
