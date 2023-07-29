import type { NextRequestWithAuth } from "next-auth/middleware";
import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  function middleware(request: NextRequestWithAuth) {
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
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

// export const config = { matcher: ["/home", "/content", "/help", "/settings"] };
export const config = { matcher: [] };
