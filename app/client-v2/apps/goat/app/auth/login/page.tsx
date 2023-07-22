"use client";

import { signIn, useSession } from "next-auth/react";
import { redirect } from "next/navigation";

export default function Login() {
  const { status, data: session } = useSession();

  if (session) {
    redirect(`/`);
  }
  if (status === "unauthenticated") {
    signIn("keycloak");
  }

  return <></>;
}
