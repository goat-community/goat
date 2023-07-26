import { manageUsersStatic } from "@/public/assets/data/dashboard";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  return NextResponse.json(manageUsersStatic);
}
