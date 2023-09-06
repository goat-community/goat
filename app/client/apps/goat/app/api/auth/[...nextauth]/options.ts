import type { KeycloakTokenSet, NextAuthOptions } from "next-auth";
import type { JWT } from "next-auth/jwt";
import KeycloakProvider from "next-auth/providers/keycloak";

const keycloak = KeycloakProvider({
  id: "keycloak",
  clientId: process.env.KEYCLOAK_CLIENT_ID as string,
  clientSecret: process.env.KEYCLOAK_CLIENT_SECRET as string,
  issuer: process.env.KEYCLOAK_ISSUER,
  authorization: { params: { scope: "openid email profile offline_access" } },
});

// this performs the final handshake for the keycloak provider
async function doFinalSignoutHandshake(token: JWT) {
  if (token.provider == keycloak.id) {
    try {
      const issuerUrl = keycloak.options?.issuer;
      const logOutUrl = new URL(`${issuerUrl}/protocol/openid-connect/logout`);
      logOutUrl.searchParams.set("id_token_hint", token.id_token);
      const { status, statusText } = await fetch(logOutUrl);
      console.log("Completed post-logout handshake", status, statusText);
    } catch {
      console.error("Unable to perform post-logout handshake");
    }
  }
}

async function getOrganization(token: JWT) {
  try {
    // eslint-disable-next-line turbo/no-undeclared-env-vars
    const url = new URL(`api/v1/users/organization`, process.env.API_URL);
    const res = await fetch(url.href, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.access_token}`,
      },
    });
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error retrieving organization: ", error);
    return null;
  }
}

async function getSubscriptions(token: JWT) {
  try {
    // eslint-disable-next-line turbo/no-undeclared-env-vars
    const url = new URL(`api/v1/users/subscriptions`, process.env.API_URL);
    const res = await fetch(url.href, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.access_token}`,
      },
    });
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error retrieving subscriptions: ", error);
    return [];
  }
}

async function refreshAccessToken(token: JWT): Promise<JWT> {
  try {
    const response = await fetch(`${keycloak.options?.issuer}/protocol/openid-connect/token`, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: keycloak.options?.clientId as string,
        client_secret: keycloak.options?.clientSecret as string,
        grant_type: "refresh_token",
        refresh_token: token.refresh_token as string,
      }),
      method: "POST",
    });

    const tokensRaw = await response.json();
    const tokens: KeycloakTokenSet = tokensRaw;
    if (!response.ok) throw tokens;

    const expiresAt = Math.floor(Date.now() / 1000 + tokens.expires_in);
    console.log(
      `Token was refreshed. New token expires in ${tokens.expires_in} sec at ${expiresAt}, refresh token expires in ${tokens.refresh_expires_in} sec`
    );
    const newToken: JWT = {
      ...token,
      access_token: tokens.access_token,
      expires_at: expiresAt,
      refresh_token: tokens.refresh_token ?? token.refresh_token,
      id_token: tokens.id_token ?? token.id_token,
      provider: keycloak.id,
    };
    const organization = await getOrganization(newToken);
    const subscriptions = await getSubscriptions(newToken);
    newToken.organization = organization ? organization.id : null;
    newToken.subscriptions = subscriptions && subscriptions.length > 0 ? subscriptions : null;
    return newToken;
  } catch (error) {
    console.error("Error refreshing access token: ", error);
    return {
      ...token,
      error: "RefreshAccessTokenError",
    };
  }
}

export const options: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  providers: [keycloak],
  pages: {
    signIn: "/auth/login",
    error: "/auth/error",
  },
  theme: {
    colorScheme: "light",
  },
  callbacks: {
    async session({ session, token }) {
      if (token) {
        session.access_token = token.access_token;
      }
      if (session.user) {
        session.user.organization = token.organization;
        session.user.subscriptions = token.subscriptions;
      }
      session.error = token.error;
      return session;
    },
    async jwt({ token, account, user }) {
      if (account && user) {
        if (!account.access_token) throw Error("Auth Provider missing access token");
        if (!account.refresh_token) throw Error("Auth Provider missing refresh token");
        if (!account.id_token) throw Error("Auth Provider missing ID token");
        const newToken: JWT = {
          ...token,
          access_token: account.access_token,
          refresh_token: account.refresh_token,
          id_token: account.id_token,
          expires_at: Math.floor(account.expires_at ?? 0),
          provider: account.provider,
        };
        const organization = await getOrganization(newToken);
        const subscriptions = await getSubscriptions(newToken);
        newToken.organization = organization ? organization.id : null;
        newToken.subscriptions = subscriptions && subscriptions.length > 0 ? subscriptions : null;
        return newToken;
      }
      if (Date.now() < token.expires_at * 1000) {
        return token;
      }
      const newToken = await refreshAccessToken(token);
      return newToken;
    },
  },
  events: {
    signOut: async ({ token }) => doFinalSignoutHandshake(token),
  },
  jwt: {
    maxAge: 1 * 60, // 1 minute, same as in Keycloak
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days : 2592000, same as in Keycloak
  },
};
