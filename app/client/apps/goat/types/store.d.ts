import type {IStylingState} from "@/lib/store/styling/slice";
import type { Expression } from "./map/filtering";
export interface IStore {
  map: object;
  content: {
    folders: [];
    getFoldersStatus: string;
    previewMode: string;
  };
  styling: IStylingState;
  mapFilters: {
    filters: { [key: string]: string };
    logicalOperator: string;
    expressions: Expression[];
  };
}
