import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { isAuthDisabled } from "@/lib/utils/auth-flag";

import type { MiddlewareFactory } from "@/middlewares/types";

const protectedPaths = [
  "/home",
  "/content",
  "/projects",
  "/datasets",
  "/settings",
  "/map",
  "/onboarding/organization/create",
  "/onboarding/organization/suspended",
  "/onboarding/organization/invite",
];

const publicPaths = ["/map/public", "/print"];

const MISSING_AUTH_CONFIG_MESSAGE =
  "Authentication is enabled but NEXTAUTH_URL / NEXTAUTH_SECRET are not set";

let missingAuthConfigLogged = false;

export const withAuth: MiddlewareFactory = (next) => {
  return async (request: NextRequest, _next) => {
    // AUTH is read at runtime (middleware runs server-side); the client bundle
    // gets the same flag as NEXT_PUBLIC_AUTH, inlined at build time.
    if (isAuthDisabled(process.env.AUTH)) {
      return next(request, _next);
    }
    const { pathname, search, origin, basePath } = request.nextUrl;

    // Skip public paths
    const isPublicPath = publicPaths.some((p) => pathname.startsWith(p));
    if (isPublicPath) return next(request, _next);

    // Skip if not protected
    const isProtected = protectedPaths.some((p) => pathname.startsWith(p));
    if (!isProtected) return next(request, _next);

    // Auth is on but NextAuth cannot verify a session: refuse instead of
    // serving protected pages unauthenticated.
    const nextAuthSecret = process.env.NEXTAUTH_SECRET;
    if (!process.env.NEXTAUTH_URL || !nextAuthSecret) {
      if (!missingAuthConfigLogged) {
        missingAuthConfigLogged = true;
        console.error(MISSING_AUTH_CONFIG_MESSAGE);
      }
      return new NextResponse(MISSING_AUTH_CONFIG_MESSAGE, { status: 500 });
    }

    const token = await getToken({ req: request, secret: nextAuthSecret });
    const isAuthorized = !!token && token.error !== "RefreshAccessTokenError";

    if (isAuthorized) {
      return next(request, _next);
    }

    // Redirect unauthorized user to login
    const signInUrl = new URL(`${basePath}/auth/login`, origin);
    signInUrl.searchParams.set("callbackUrl", `${basePath}${pathname}${search}`);
    return NextResponse.redirect(signInUrl);
  };
};
