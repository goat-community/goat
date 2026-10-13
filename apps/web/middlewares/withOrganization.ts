import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { isAuthDisabled } from "@/lib/utils/auth-flag";
import { publicEnv } from "@/lib/utils/public-env";
import type { InvitationPaginated } from "@/lib/validations/invitation";
import type { OrganizationCreation } from "@/lib/validations/organization";

import { refreshAccessToken } from "@/app/api/auth/[...nextauth]/options";
import type { MiddlewareFactory } from "@/middlewares/types";

const protectedPaths = ["/home", "/content", "/projects", "/datasets", "/settings", "/map"];
const publicPaths = ["/map/public"];

export const withOrganization: MiddlewareFactory = (next) => {
  return async (request: NextRequest, _next) => {
    // AUTH is read at runtime (middleware runs server-side); the client bundle
    // gets the same flag as NEXT_PUBLIC_AUTH, inlined at build time.
    // API_URL (runtime, e.g. a cluster-internal URL) overrides the public API
    // URL inlined at build time.
    const apiUrl = process.env.API_URL || publicEnv(process.env.NEXT_PUBLIC_API_URL);
    if (
      isAuthDisabled(process.env.AUTH) ||
      !process.env.NEXTAUTH_URL ||
      !process.env.NEXTAUTH_SECRET ||
      !apiUrl
    ) {
      return next(request, _next);
    }

    const USERS_API_BASE_URL = new URL("api/v2/users", apiUrl).href;

    const { pathname, origin, basePath } = request.nextUrl;

    // Skip public paths
    const isPublicPath = publicPaths.some((p) => pathname.startsWith(p));
    if (isPublicPath) return next(request, _next);

    // Skip unprotected paths
    const isProtected = protectedPaths.some((p) => pathname.startsWith(p));
    if (!isProtected) return next(request, _next);

    const token = await getToken({
      req: request,
      secret: process.env.NEXTAUTH_SECRET,
    });
    if (!token) return next(request, _next);

    try {
      let _token = token;

      // Refresh expired token
      if (Date.now() >= token.expires_at * 1000) {
        _token = await refreshAccessToken(token);
      }

      // Check user's organization status
      const orgRes = await fetch(`${USERS_API_BASE_URL}/organization`, {
        headers: {
          Authorization: `Bearer ${_token.access_token}`,
        },
      });

      if (orgRes.ok) {
        const organization = await orgRes.json();

        // Suspended org
        if (organization?.suspended) {
          return NextResponse.redirect(new URL(`${basePath}/onboarding/organization/suspended`, origin));
        }

        // Valid org
        if (organization?.id) {
          const response = (await next(request, _next)) as NextResponse;
          response.cookies.set("organization", organization.id, { path: "/" });
          return response;
        }
      }

      // No organization: a pending invitation opens, otherwise the setup form,
      // unless core lets only administrators create organizations. Both are
      // asked at once. A failed answer about creation counts as none: the form
      // is shown, and core refuses the creation itself.
      const headers = { Authorization: `Bearer ${_token.access_token}` };
      const [invitationRes, creationRes] = await Promise.all([
        fetch(`${USERS_API_BASE_URL}/invitations?type=organization&status=pending`, { headers }),
        fetch(`${USERS_API_BASE_URL}/me/organization-creation`, { headers }).catch(() => null),
      ]);

      if (invitationRes.ok) {
        const invitations: InvitationPaginated = await invitationRes.json();
        if (invitations?.items?.length > 0) {
          const firstInvitationId = invitations.items[0].id;
          return NextResponse.redirect(
            new URL(`${basePath}/onboarding/organization/invite/${firstInvitationId}`, origin)
          );
        }
      }

      if (creationRes?.ok) {
        const creation: OrganizationCreation = await creationRes.json();
        if (creation?.allowed === false) {
          return NextResponse.redirect(new URL(`${basePath}/onboarding/organization/waiting`, origin));
        }
      }
    } catch (error) {
      console.error("Error while fetching organization", error);
    }

    // No org or invite → redirect to create org page
    const createUrl = new URL(`${basePath}/onboarding/organization/create`, origin);
    return NextResponse.redirect(createUrl);
  };
};
