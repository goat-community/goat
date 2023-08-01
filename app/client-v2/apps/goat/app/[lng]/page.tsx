import { redirect } from "next/navigation";

export default async function Home({ params: { lng } }) {
  return redirect(`${lng}/home`);
}
