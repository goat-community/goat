import { options as authOptions } from "@/app/api/auth/[...nextauth]/options";
import type { Session } from "next-auth";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

export default async function Home({}) {
  const session: Session | null = await getServerSession(authOptions);
  if (!session) {
    redirect("/api/auth/signin");
  }

  if (session?.user && !session?.user?.org_id) {
    return redirect(`/onboarding`);
  }

  return redirect(`/home`);
}
