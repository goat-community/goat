import type { ContentState } from "@/lib/store/content/slice";
import type { LayerState } from "@/lib/store/layer/slice";
import type { MapState } from "@/lib/store/map/slice";

import type { Expression } from "./map/filtering";

export interface IStore {
  map: MapState;
  content: ContentState;
  mapFilters: {
    filters: { [key: string]: string };
    logicalOperator: string;
    expressions: Expression[];
    layerToBeFiltered: string;
  };
  layers: LayerState;
}
