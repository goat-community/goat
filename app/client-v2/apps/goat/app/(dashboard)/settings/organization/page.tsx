import { redirect } from "next/navigation";

import "../../../../styles/globals.css";

export default async function Organization({}) {
  // return (<p>hello</p>)
  return redirect("/settings/organization");
}