import type { NextAuthOptions } from "next-auth";
import KeycloakProvider from "next-auth/providers/keycloak";

export const options: NextAuthOptions = {
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_ID as string,
      clientSecret: process.env.KEYCLOAK_SECRET as string,
      issuer: process.env.KEYCLOAK_ISSUER,
    }),
  ],
};
