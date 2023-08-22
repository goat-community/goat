import { options as authOptions } from "@/app/api/auth/[...nextauth]/options";
import { responses } from "@/lib/api/response";
import { getServerSession } from "next-auth";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { z } from "zod";

const routeContextSchema = z.object({
  params: z.object({
    organizationId: z.string(),
  }),
});

export async function GET(_req: NextRequest, context: z.infer<typeof routeContextSchema>) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || !session.access_token) {
      return responses.notAuthenticatedResponse();
    }
    const { params } = routeContextSchema.parse(context);
    const url = new URL(`api/v1/organizations/${params.organizationId}`, process.env.API_URL);
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
