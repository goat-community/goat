import { redirect } from "next/navigation";

import "../../../styles/globals.css";

export default async function Home({}) {
  return redirect("/settings/organization");
}
