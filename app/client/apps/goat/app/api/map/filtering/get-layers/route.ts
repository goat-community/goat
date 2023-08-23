import type { LayerData } from "@/types/map/filtering";
import { NextResponse } from "next/server";

const url = "http://127.0.0.1:8081";

export async function GET() {
  try {
    const res = await fetch(`${url}/collections`);

    const layers: LayerData = await res.json();

    return NextResponse.json(layers);
  } catch (error) {
    console.error("Error fetching data:", error);
    return new NextResponse("Error fetching data from the data source.", {
      status: 500, // You can adjust the status code as needed
    });
  }
}
