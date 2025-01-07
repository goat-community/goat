import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";
import { type NextFetchEvent, type NextMiddleware, NextResponse } from "next/server";

import { cookieName, fallbackLng } from "@/i18n/settings";

import type { MiddlewareFactory } from "@/middlewares/types";

const protectedPaths = ["/home", "/projects", "datasets", "/settings", "/map", "/onboarding/organization/create", "/onboarding/organization/suspended"];
const publicPaths = ["/map/public"];

export const withAuth: MiddlewareFactory = (next: NextMiddleware) => {
  return async (request: NextRequest, _next: NextFetchEvent) => {
    const { pathname, search, origin, basePath } = request.nextUrl;



    // check language cookie. The url in this case will be /:lng/:path
    const lng = request.cookies.get(cookieName)?.value;
    const lngPath = lng ? `/${lng}` : fallbackLng ? `/${fallbackLng}` : "";
    const signInPage = `${lngPath}/auth/login/`;
    const errorPage = `${lngPath}/auth/error/`;

    // Remove language prefix from pathname for public path check
    const strippedPathname = pathname.startsWith(lngPath) ? pathname.slice(lngPath.length) : pathname;
    // Check if the path is public
    const isPublicPath = publicPaths.some((p) => strippedPathname.startsWith(p));
    if (isPublicPath) {
      return await next(request, _next);
    }

    const _protectedPaths = protectedPaths.map((p) => (lngPath ? `${lngPath}${p}` : p));

    if (!_protectedPaths.some((p) => pathname.startsWith(p))) return await next(request, _next);

    const nextAuthSecret = process.env.NEXTAUTH_SECRET;
    if (!nextAuthSecret) {
      console.error(`[next-auth][error][NO_SECRET]`, `\nhttps://next-auth.js.org/errors#no_secret`);
      const errorUrl = new URL(`${basePath}${errorPage}`, origin);
      errorUrl.searchParams.append("error", "Configuration");

      return NextResponse.redirect(errorUrl);
    }

    const token = await getToken({
      req: request,
      secret: nextAuthSecret,
    });
    const isAuthorized = !!token && token.error !== "RefreshAccessTokenError";


    // the user is authorized, let the middleware handle the rest
    if (isAuthorized) return await next(request, _next);

    // the user is not logged in, redirect to the sign-in page
    const signInUrl = new URL(`${basePath}${signInPage}`, origin);
    signInUrl.searchParams.append("callbackUrl", `${basePath}${pathname}${search}`);
    return NextResponse.redirect(signInUrl);
  };
};
