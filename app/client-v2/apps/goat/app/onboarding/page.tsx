import { redirect } from "next/navigation";

export default async function OnBoardingPage({}) {
  return redirect("/onboarding/organization");
}
