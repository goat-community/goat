import { options } from "@/app/[lng]/api/auth/[...nextauth]/options";
import UserCard from "@/app/[lng]/components/UserCard";
import { getServerSession } from "next-auth/next";
import { redirect } from "next/navigation";

export default async function ServerPage() {
  const session = await getServerSession(options);

  if (!session) {
    redirect("/api/auth/signin?callbackUrl=/server");
  }

  return (
    <section className="flex flex-col gap-6">
      <UserCard user={session?.user} pagetype="Server" />
    </section>
  );
}
