// todo check
import { fallbackLng, languages } from "@/app/i18/settings";
import acceptLanguage from "accept-language";
import type { NextRequestWithAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

acceptLanguage.languages(languages);

export const config = {
  // matcher: '/:lng*'
  matcher: ["/((?!api|_next/static|_next/image|assets|favicon.ico|sw.js).*)"],
};

const cookieName = "i18next";

// export default withAuth(
export default function middleware(request: NextRequestWithAuth) {
  let lng;
  if (request.cookies.has(cookieName)) lng = acceptLanguage.get(request.cookies.get(cookieName).value);
  if (!lng) lng = acceptLanguage.get(request.headers.get("Accept-Language"));
  if (!lng) lng = fallbackLng;

  // Redirect if lng in path is not supported
  if (
    !languages.some((loc) => request.nextUrl.pathname.startsWith(`/${loc}`)) &&
    !request.nextUrl.pathname.startsWith("/_next")
  ) {
    return NextResponse.redirect(new URL(`/${lng}${request.nextUrl.pathname}`, request.url));
  }

  if (request.headers.has("referer")) {
    const refererUrl = new URL(request.headers.get("referer"));
    const lngInReferer = languages.find((l) => refererUrl.pathname.startsWith(`/${l}`));
    const response = NextResponse.next();
    if (lngInReferer) response.cookies.set(cookieName, lngInReferer);
    return response;
  }

  // const pathname = request.nextUrl.pathname;
  // if (!request.nextauth.token || request.nextauth.token.error === "RefreshAccessTokenError") {
  //   const url = new URL(`/${lng}/api/auth/signin`, request.url);
  //   console.log("aaa", url);
  //   url.searchParams.set("callbackUrl", encodeURI(request.url));
  //   return NextResponse.redirect(url);
  // }
  //
  // if (!request.nextauth.token?.organization && pathname !== `/${lng}/auth/organization`) {
  //   const url = new URL(`/${lng}/auth/organization`, request.url);
  //   return NextResponse.redirect(url);
  // }
  //
  // if (pathname === `/${lng}/auth/organization`) {
  //   const url = new URL(`/${lng}/home`, request.url);
  //   return NextResponse.redirect(url);
  // }

  return NextResponse.next();
}
// {
//   callbacks: {
//     authorized: ({ token }) => !!token,
//   },
// }
// );

// // export const config = { matcher: ["/home", "/content", "/help", "/settings"] };
// export const config = { matcher: [] };
// end todo
