import AuthCheck from "@/components/AuthCheck";
import ThemeRegistry from "@/lib/ThemeRegistry";
import AuthProvider from "@/lib/context/AuthProvider";
import Provider from "@/lib/context/StoreProvider";
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
      <body>
        <Provider>
          <AuthProvider>
            <AuthCheck />
            <ThemeRegistry>{children}</ThemeRegistry>
          </AuthProvider>
        </Provider>
      </body>
    </html>
  );
}
