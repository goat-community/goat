import { Metadata } from "next/types"
import { MuiSetup } from "./MuiSetup"

export const metadata: Metadata = {
  title: "My title",
  description: "My description",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <MuiSetup>{children}</MuiSetup>
      </body>
    </html>
  )
}
