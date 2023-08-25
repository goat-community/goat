import { NextResponse } from "next/server";
import { dummyOrganization } from "@/public/assets/data/dashboard";

export async function GET() {
  return NextResponse.json(dummyOrganization);
}
