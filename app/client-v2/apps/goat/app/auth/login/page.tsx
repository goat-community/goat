"use client";

import { signIn, useSession } from "next-auth/react";
import { redirect } from "next/navigation";

export default function Login() {
  const { status, data: session } = useSession();
  console.log("session", session);
  if (status === "unauthenticated" || session?.error === "RefreshAccessTokenError") {
    signIn("keycloak");
  }
  if (session && session?.error !== "RefreshAccessTokenError") {
    redirect(`/`);
  }

  return <></>;
}
