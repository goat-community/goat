import { type APIRequestContext, type Page, type TestType, request, test } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

/**
 * The test users and how specs act as them.
 *
 * With auth on (`E2E_AUTH`, set by the CI workflow), `scripts/e2e/provision.py`
 * has created one user per role and written them to `.auth/users.json`, and
 * `auth.setup.ts` has logged each one in and saved the session next to it.
 * With auth off every request is the built-in development user, and only
 * the owner's view exists: role-specific specs skip themselves.
 */

export type Role = "owner" | "admin" | "editor" | "editor2" | "viewer" | "outsider" | "newcomer" | "invitee";

/** Roles with a saved browser session; newcomer and invitee log in inside
 * the specs that test their first login. editor2 is a second editor of the
 * owner's organization, for specs that need two members to act
 * independently (e.g. two users of one template). */
export const SESSION_ROLES: Role[] = ["owner", "admin", "editor", "editor2", "viewer", "outsider"];

export const AUTH_ON = !!process.env.E2E_AUTH;

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const AUTH_DIR = path.join(__dirname, "..", ".auth");

export const storageStatePath = (role: Role): string => path.join(AUTH_DIR, `${role}.json`);

type CastUser = { id: string; email: string; firstname: string; lastname: string };
type Cast = {
  organization_id: string;
  outsider_organization_id: string;
  users: Record<Role, CastUser>;
  /** The owner's datasets, uploaded and imported by the provisioning. */
  datasets: Record<"points" | "table" | "editable", string>;
};

/** The provisioned users' password: the CI run sets a fresh one, and both
 * `provision.py` and the specs read it from the environment, so it is never
 * written to disk. */
export const PASSWORD = process.env.E2E_PASSWORD ?? "E2e-Passw0rd!";

let cast: Cast | undefined;

/** The provisioned users (auth on only). */
export const castOf = (): Cast => {
  cast ??= JSON.parse(fs.readFileSync(path.join(AUTH_DIR, "users.json"), "utf8")) as Cast;
  return cast;
};

export const userOf = (role: Role): CastUser => castOf().users[role];

/** A fresh access token for a role, from Keycloak's password grant. Tokens
 * live five minutes, longer than any spec's API work. */
const accessToken = async (role: Role): Promise<string> => {
  const issuer = `${process.env.KEYCLOAK_SERVER_URL}/realms/${process.env.REALM_NAME}`;
  const context = await request.newContext();
  try {
    const response = await context.post(`${issuer}/protocol/openid-connect/token`, {
      form: {
        grant_type: "password",
        client_id: process.env.KEYCLOAK_CLIENT_ID ?? "goat",
        client_secret: process.env.KEYCLOAK_CLIENT_SECRET ?? "",
        username: userOf(role).email,
        password: PASSWORD,
        scope: "openid",
      },
    });
    if (!response.ok()) throw new Error(`token for ${role}: ${response.status()} ${await response.text()}`);
    return ((await response.json()) as { access_token: string }).access_token;
  } finally {
    await context.dispose();
  }
};

/** An API client acting as `role` (the built-in user with auth off). */
export const apiAs = async (role: Role = "owner"): Promise<APIRequestContext> =>
  request.newContext({
    extraHTTPHeaders: AUTH_ON ? { Authorization: `Bearer ${await accessToken(role)}` } : {},
  });

/** Runs the specs of the calling file as `role`. With auth off, a role other
 * than the owner cannot be acted as, so those specs are skipped. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const actAs = (test: TestType<any, any>, role: Role): void => {
  if (!AUTH_ON) {
    test.skip(role !== "owner", `needs auth on to act as ${role}`);
    return;
  }
  test.use({ storageState: storageStatePath(role) });
};

/** Skips the calling file's specs unless auth is on. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const needsAuth = (test: TestType<any, any>): void => {
  test.skip(!AUTH_ON, "needs auth on (Keycloak and the provisioned users)");
};

/** Signs in on Keycloak's login page, which every protected page sends an
 * anonymous visitor to, and waits to be back in the app. */
export const logIn = async (page: Page, email: string, password: string): Promise<void> => {
  await page.goto("/home");
  await page.locator("input[name=username]").fill(email);
  await page.locator("input[name=password]").fill(password);
  await page.locator("button[name=login]").click();
  // Back in the app (CI: port 3000) from Keycloak's page (CI: port 8080). A
  // stack that serves Keycloak on the app's own port (the config's baseURL) is told
  // apart by Keycloak's /realms/ paths.
  const appPort = new URL(test.info().project.use.baseURL ?? "http://localhost:3000/").port;
  await page.waitForURL((url) => url.port === appPort && !url.pathname.startsWith("/realms/"), {
    timeout: 30000,
  });
};
