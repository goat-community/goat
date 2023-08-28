import { dummySubscription, extensionSubscriptions } from "@/public/assets/data/dashboard";
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    subscription: dummySubscription,
    extensions: extensionSubscriptions,
  });
}
