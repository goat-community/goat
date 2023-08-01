import { fallbackLng, languages } from "@/app/i18/settings";
import acceptLanguage from "accept-language";
import type { NextRequestWithAuth } from "next-auth/middleware";
import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

acceptLanguage.languages(languages);

const cookieName = "i18next";

// First Middleware Function
function authMiddleware(request: NextRequestWithAuth) {
  const pathname = request.nextUrl.pathname;
  if (!request.nextauth.token || request.nextauth.token.error === "RefreshAccessTokenError") {
    const url = new URL(`/api/auth/signin`, request.url);
    url.searchParams.set("callbackUrl", encodeURI(request.url));
    return NextResponse.redirect(url);
  }

  if (!request.nextauth.token?.organization && pathname !== "/auth/organization") {
    const url = new URL("/auth/organization", request.url);
    return NextResponse.redirect(url);
  }

  if (pathname === "/auth/organization") {
    const url = new URL("/home", request.url);
    return NextResponse.redirect(url);
  }

  return NextResponse.next(); // Make sure to return a response if no redirect is needed
}

// Second Middleware Function
function i18nMiddleware(req) {
  let lng;
  if (req.cookies.has(cookieName)) lng = acceptLanguage.get(req.cookies.get(cookieName).value);
  if (!lng) lng = acceptLanguage.get(req.headers.get("Accept-Language"));
  if (!lng) lng = fallbackLng;

  // Redirect if lng in path is not supported
  if (
    !languages.some((loc) => req.nextUrl.pathname.startsWith(`/${loc}`)) &&
    !req.nextUrl.pathname.startsWith("/_next")
  ) {
    return NextResponse.redirect(new URL(`/${lng}${req.nextUrl.pathname}`, req.url));
  }

  if (req.headers.has("referer")) {
    const refererUrl = new URL(req.headers.get("referer"));
    const lngInReferer = languages.find((l) => refererUrl.pathname.startsWith(`/${l}`));
    const response = NextResponse.next();
    if (lngInReferer) response.cookies.set(cookieName, lngInReferer);
    return response;
  }

  return NextResponse.next(); // Make sure to return a response if no redirect is needed
}

// Combined Middleware Function
const combinedMiddleware = withAuth(
  function middleware(request: NextRequestWithAuth) {
    // Call both middleware functions and return the response
    const authResponse = authMiddleware(request);
    return i18nMiddleware(authResponse || request);
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

export default combinedMiddleware;

export const config = { matcher: [] };
