import type { Layer } from "@/lib/validations/layer";
import type { MapGeoJSONFeature } from "react-map-gl/maplibre";


export enum EditorModes {
  DRAW = "draw",
  MODIFY_GEOMETRY = "modify_geometry",
  MODIFY_ATTRIBUTES = "modify_attributes",
  DELETE = "delete",
}

export type MapPopoverEditorProps = {
  title?: string;
  lngLat: [number, number];
  feature?: MapGeoJSONFeature | undefined;
  editMode: EditorModes;
  layer: Layer;
  onClose: () => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onConfirm: (payload: any) => void;
};

export type MapPopoverInfoProps = {
  title: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  properties: { [name: string]: any } | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  jsonProperties: { [name: string]: any } | null;
  lngLat: [number, number];
  onClose: () => void;
};

