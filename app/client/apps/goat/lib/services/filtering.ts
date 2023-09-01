import axios from "axios";

export async function filterUsingQuery(query: string | undefined, layer_id: string, url: string) {
  try {
    if(query){
      const res = await axios({
        url: `${url}${layer_id}`,
        method: "POST",
        data: {
          query_filter: JSON.parse(query),
        },
      });
      return res.data;
    }else{
      return {error: "query is invalid"}
    }
  } catch (error) {
    console.error(error);
    return null;
  }
}
