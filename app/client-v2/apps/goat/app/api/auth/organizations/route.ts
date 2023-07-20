import { responses } from "@/lib/api/response";
import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { z } from "zod";

export async function GET(req: NextRequest) {
  try {
    const token = await getToken({ req });
    if (!token || !token.accessToken) {
      return responses.notAuthenticatedResponse();
    }
    console.log(token);
    const url = new URL("api/v1/organizations", process.env.API_URL);
    console.log(url.href);
    const res = await fetch(url.href, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.accessToken}`,
      },
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(error);
    if (error instanceof z.ZodError) {
      return new Response(JSON.stringify(error.issues), { status: 422 });
    }
    return new Response(null, { status: 500 });
  }
}
