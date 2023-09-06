import { options as authOptions } from "@/app/api/auth/[...nextauth]/options";
import { responses } from "@/lib/api/response";
import { postOrganizationSchema } from "@/lib/validations/organization";
import { getServerSession } from "next-auth";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { z } from "zod";

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session || !session.access_token) {
      return responses.notAuthenticatedResponse();
    }
    // eslint-disable-next-line turbo/no-undeclared-env-vars
    const url = new URL("api/v1/organizations", process.env.API_URL);
    console.log(url.href);
    const res = await fetch(url.href, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error(error);
    if (error instanceof z.ZodError) {
      return new Response(JSON.stringify(error.issues), { status: 422 });
    }
    return new Response(null, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session || !session.access_token) {
      return responses.notAuthenticatedResponse();
    }
    // eslint-disable-next-line turbo/no-undeclared-env-vars
    const url = new URL("api/v1/organizations", process.env.API_URL);
    const body = await req.json();
    const payload = postOrganizationSchema.parse(body);
    const res = await fetch(url.href, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error(error);
    if (error instanceof z.ZodError) {
      return new Response(JSON.stringify(error.issues), { status: 422 });
    }
    return new Response(null, { status: 500 });
  }
}
