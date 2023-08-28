import axios from "axios";

export async function filterUsingQuery(query: string, layer_id: string, url: string) {
  try {
    const res = await axios({
      url: `${url}${layer_id}`,
      method: "POST",
      data: {
        query_filter: JSON.parse(query),
      },
    });
    return res.data;
  } catch (error) {
    console.error(error);
    return null;
  }
}
