import acceptLanguage from "accept-language";
import { NextResponse } from "next/server";
import type { NextFetchEvent, NextMiddleware, NextRequest } from "next/server";

import { fallbackLng, languages, cookieName as lngCookieName } from "@/i18n/settings";

import type { MiddlewareFactory } from "./types";

acceptLanguage.languages(languages);

const excluded = ["/api", "/_next/static", "/_next/image", "/assets", "/favicon.ico", "/sw.js"];
export const withLanguage: MiddlewareFactory = (next: NextMiddleware) => {
  return async (request: NextRequest, _next: NextFetchEvent) => {
    const { pathname } = request.nextUrl;

    if (excluded.some((path) => pathname.startsWith(path))) return next(request, _next);

    // Language redirect
    let lng;
    if (request.cookies.has(lngCookieName))
      lng = acceptLanguage.get(request.cookies.get(lngCookieName)?.value);
    if (!lng) lng = acceptLanguage.get(request.headers.get("Accept-Language"));
    if (!lng) lng = fallbackLng;
    if (!languages.some((loc) => pathname.startsWith(`/${loc}`)) && !pathname.startsWith("/_next")) {
      return NextResponse.redirect(new URL(`/${lng}${pathname}`, request.url));
    }
    if (request.headers.has("referer")) {
      const refererUrl = new URL(request.headers.get("referer") as string);
      const lngInReferer = languages.find((l) => refererUrl.pathname.startsWith(`/${l}`));
      const response = (await next(request, _next)) as NextResponse;
      if (response && lngInReferer) response.cookies.set(lngCookieName, lngInReferer);
      return response;
    }

    return next(request, _next);
  };
};
