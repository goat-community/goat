import { Inter } from "next/font/google";

import Navbar from "./components/Navbar";
import AuthProvider from "./context/AuthProvider";
import Providers from "./context/Provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "NextAuth Tutorial",
  description: "Learn NextAuth.js by Dave Gray",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <AuthProvider>
            <Navbar />
            <main className="flex justify-center items-start p-6 min-h-screen">{children}</main>
          </AuthProvider>
        </Providers>
      </body>
    </html>
  );
}
