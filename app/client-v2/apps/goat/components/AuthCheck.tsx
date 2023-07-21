"use client";

import { useSession } from "next-auth/react";
import { useEffect } from "react";

export default function AuthCheck() {
  const result = useSession();
  console.log("session", result);
  useEffect(() => {
    console.log("session", result);

    // if (result?.error === "RefreshAccessTokenError") {
    //   signIn("keycloak");
    // }
  }, [result]);
  return <></>;
}
