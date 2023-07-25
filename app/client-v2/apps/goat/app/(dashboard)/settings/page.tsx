import "@/styles/globals.css";
import { redirect } from "next/navigation";

export default async function Home({}) {
  return redirect("/settings/organization");
}
