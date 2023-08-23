import type { LayerData } from "@/types/map/filtering";
import { NextResponse } from "next/server";

const url = "http://127.0.0.1:8081";

export async function POST(request: Request) {
  const layer_id = request.url.slice(request.url.lastIndexOf("/") + 1);

  try {
    const { query_filter } = await request.json();
    const res = await fetch(`${url}/collections/${layer_id}/items?filter=${JSON.stringify(query_filter)}`);
    const features = await res.json();

    return NextResponse.json(features);
  } catch (e) {
    const res = await fetch(`${url}/collections/${layer_id}/items?limit=100`);
    const features: LayerData = await res.json();
    return NextResponse.json(features);
  }
}
