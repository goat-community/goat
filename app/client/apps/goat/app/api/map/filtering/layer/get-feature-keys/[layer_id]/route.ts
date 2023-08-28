import { NextResponse } from "next/server";

const url = "http://127.0.0.1:8081";

export async function GET(request: Request) {
  const layer_id = request.url.slice(request.url.lastIndexOf("/") + 1);
  console.log(layer_id);
  try {
    const res = await fetch(`${url}/collections/${layer_id}/queryables`);

    const keys = await res.json();

    return NextResponse.json(keys);
  } catch (error) {
    console.error("Error fetching data:", error);
    return new NextResponse("Error fetching data from the data source.", {
      status: 500, // You can adjust the status code as needed
    });
  }
}
