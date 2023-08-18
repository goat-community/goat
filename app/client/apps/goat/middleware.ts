// todo check
// import type { NextRequestWithAuth } from "next-auth/middleware";
// import { withAuth } from "next-auth/middleware";
// import { NextResponse } from "next/server";
//
// export default withAuth(
//   function middleware(request: NextRequestWithAuth) {
//     const pathname = request.nextUrl.pathname;
//     if (!request.nextauth.token || request.nextauth.token.error === "RefreshAccessTokenError") {
//       const url = new URL(`/api/auth/signin`, request.url);
//       url.searchParams.set("callbackUrl", encodeURI(request.url));
//       return NextResponse.redirect(url);
//     }
//
//     if (!request.nextauth.token?.organization && pathname !== "/auth/organization") {
//       const url = new URL("/auth/organization", request.url);
//       return NextResponse.redirect(url);
//     }
//
//     if (pathname === "/auth/organization") {
//       const url = new URL("/home", request.url);
//       return NextResponse.redirect(url);
//     }
//
//   },
//   {
//     callbacks: {
//       authorized: ({ token }) => !!token,
//     },
//   }
// );
//
// // export const config = { matcher: ["/home", "/content", "/help", "/settings"] };
// export const config = { matcher: [] };
// end todo
import { fallbackLng, languages } from "@/app/i18/settings";
import acceptLanguage from "accept-language";
import { NextResponse } from "next/server";

acceptLanguage.languages(languages);

export const config = {
  // matcher: '/:lng*'
  matcher: ["/((?!api|_next/static|_next/image|assets|favicon.ico|sw.js).*)"],
};

const cookieName = "i18next";

export function middleware(req) {
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

  return NextResponse.next();
}
