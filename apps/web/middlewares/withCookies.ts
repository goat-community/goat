import { getToken } from "next-auth/jwt";
import type { NextFetchEvent, NextMiddleware, NextRequest, NextResponse } from "next/server";

import { cookieName as lngCookieName } from "@/i18n/settings";

import { THEME_COOKIE_NAME as themeCookieName } from "@/lib/constants";

import { refreshAccessToken } from "@/app/api/auth/[...nextauth]/options";

import type { MiddlewareFactory } from "./types";

export const SYSTEM_API_BASE_URL = new URL("api/v2/system", process.env.NEXT_PUBLIC_API_URL).href;

const excluded = ["/api", "/_next/static", "/_next/image", "/assets", "/favicon.ico", "/sw.js"];
export const withCookies: MiddlewareFactory = (next: NextMiddleware) => {
  return async (request: NextRequest, _next: NextFetchEvent) => {
    const { pathname } = request.nextUrl;

    if (excluded.some((path) => pathname.startsWith(path))) return next(request, _next);

    // Check for cookies. If not present, try to load theme from the api (!when logged in)
    const nextAuthSecret = process.env.NEXTAUTH_SECRET;
    if ((!request.cookies.has(themeCookieName) || !request.cookies.has(lngCookieName)) && nextAuthSecret) {
      const token = await getToken({
        req: request,
        secret: nextAuthSecret,
      });
      const isAuthorized = !!token;
      if (isAuthorized) {
        let _token = token;
        if (Date.now() >= token.expires_at * 1000) {
          _token = await refreshAccessToken(token);
        }
        try {
          // System Preferences cookies
          const systemPreferences = await fetch(`${SYSTEM_API_BASE_URL}/settings`, {
            headers: {
              Authorization: `Bearer ${_token.access_token}`,
            },
          });
          if (systemPreferences.ok) {
            const preferences = await systemPreferences.json();
            const response = (await next(request, _next)) as NextResponse;
            const expirationDate = new Date(Date.now() + 10 * 60 * 1000);
            if (preferences?.client_theme)
              response.cookies.set(themeCookieName, preferences.client_theme, {
                expires: expirationDate,
              });
            if (preferences?.preferred_language)
              response.cookies.set(lngCookieName, preferences.preferred_language, {
                expires: expirationDate,
              });
            return response;
          }
        } catch (error) {
          console.log("Error loading preferences from api", error);
        }
      }
    }

    return next(request, _next);
  };
};
