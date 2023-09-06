import type {
  LayerPropsMode, //KeyDataType
} from "@/types/map/filtering";
import axios from "axios";
import { useState, useEffect } from "react";

export const useGetKeys = ({ layer_id }: { layer_id: string }) => {
  const [keys, setkeys] = useState<LayerPropsMode[]>([]);
  
  useEffect(() => {
    axios.get(`http://localhost:3000/api/map/filtering/layer/get-feature-keys/${layer_id}`).then((data) => {
      const keys = data.data.properties;
      const extractedProperties = Object.keys(keys)
        .filter((key) => "name" in keys[key])
        .map((key) => {
          return { name: keys[key].name, type: keys[key].type };
        });

      setkeys(extractedProperties);
    });
  }, [layer_id]);

  return { keys };
};
