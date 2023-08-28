import { NextResponse } from "next/server";
import { manageUsersStatic } from "@/public/assets/data/dashboard";

export async function GET() {
  return NextResponse.json(manageUsersStatic);
}
