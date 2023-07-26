import { redirect } from "next/navigation";

export default async function Organization({}) {
  // return (<p>hello</p>)
  return redirect("/settings/organization");
}
