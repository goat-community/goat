import type { NextFetchEvent } from "next/server";
import { NextRequest, NextResponse } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { withOrganization } from "@/middlewares/withOrganization";

vi.mock("next-auth/jwt", () => ({
  getToken: vi.fn(async () => ({
    access_token: "access-token",
    expires_at: Math.floor(Date.now() / 1000) + 3600,
  })),
}));
vi.mock("@/app/api/auth/[...nextauth]/options", () => ({
  refreshAccessToken: vi.fn(),
}));

const CORE = "http://core.test";
const INVITATION_ID = "7a1c2e9b-3f4d-4b5a-8c6d-0e1f2a3b4c5d";

const next = vi.fn(async () => NextResponse.next());
const middleware = withOrganization(next);

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const NO_ORGANIZATION = () => json(404, { detail: "User has no organization" });
const NO_INVITATIONS = () => json(200, { items: [], total: 0, page: 1, size: 50, pages: 0 });
const AN_INVITATION = () =>
  json(200, { items: [{ id: INVITATION_ID }], total: 1, page: 1, size: 50, pages: 1 });

/** Core as the middleware sees it: one answer per route it asks. */
function core(answers: {
  organization?: () => Response;
  invitations?: () => Response | Promise<Response>;
  creation?: () => Response;
}) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url === `${CORE}/api/v2/users/organization`) return (answers.organization ?? NO_ORGANIZATION)();
    if (url.startsWith(`${CORE}/api/v2/users/invitations`)) return (answers.invitations ?? NO_INVITATIONS)();
    if (url === `${CORE}/api/v2/users/me/organization-creation`) {
      if (!answers.creation) throw new Error("organization creation was not expected to be asked");
      return answers.creation();
    }
    throw new Error(`unexpected request ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function landing(path = "/home"): Promise<string | null> {
  const res = await middleware(new NextRequest(`http://goat.test${path}`), {} as NextFetchEvent);
  const location = res?.headers.get("location");
  return location ? new URL(location).pathname : null;
}

beforeEach(() => {
  vi.stubEnv("AUTH", "true");
  vi.stubEnv("NEXTAUTH_URL", "http://goat.test");
  vi.stubEnv("NEXTAUTH_SECRET", "secret");
  vi.stubEnv("API_URL", CORE);
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  next.mockClear();
});

describe("withOrganization for a user without an organization", () => {
  it("opens the setup form when the user may create an organization", async () => {
    core({ creation: () => json(200, { allowed: true }) });
    expect(await landing()).toBe("/onboarding/organization/create");
  });

  it("opens the waiting page when only administrators create organizations", async () => {
    core({ creation: () => json(200, { allowed: false }) });
    expect(await landing()).toBe("/onboarding/organization/waiting");
    expect(next).not.toHaveBeenCalled();
  });

  it("falls back to the setup form when core does not answer the question", async () => {
    core({ creation: () => json(502, { detail: "Bad gateway" }) });
    expect(await landing()).toBe("/onboarding/organization/create");
  });

  it("falls back to the setup form when the request fails", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    core({
      creation: () => {
        throw new TypeError("fetch failed");
      },
    });
    expect(await landing()).toBe("/onboarding/organization/create");
  });

  it("opens a pending invitation even where only administrators create organizations", async () => {
    core({ invitations: AN_INVITATION, creation: () => json(200, { allowed: false }) });
    expect(await landing()).toBe(`/onboarding/organization/invite/${INVITATION_ID}`);
  });

  it("opens a pending invitation when the answer about creation fails", async () => {
    core({
      invitations: AN_INVITATION,
      creation: () => {
        throw new TypeError("fetch failed");
      },
    });
    expect(await landing()).toBe(`/onboarding/organization/invite/${INVITATION_ID}`);
  });

  it("asks about invitations and creation at once", async () => {
    let answerInvitations: () => void = () => {};
    const invitationsAnswered = new Promise<void>((resolve) => {
      answerInvitations = resolve;
    });
    const fetchMock = core({
      invitations: () => invitationsAnswered.then(NO_INVITATIONS),
      creation: () => json(200, { allowed: false }),
    });

    const landed = landing();
    // The question about creation goes out while invitations are still open.
    await vi.waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        `${CORE}/api/v2/users/me/organization-creation`,
        expect.anything()
      )
    );
    answerInvitations();

    expect(await landed).toBe("/onboarding/organization/waiting");
  });
});

describe("withOrganization for a member", () => {
  it("lets the request through without asking about creation", async () => {
    const fetchMock = core({ organization: () => json(200, { id: "org-1", suspended: false }) });
    expect(await landing()).toBeNull();
    expect(next).toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
