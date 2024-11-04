import type { Marker, MarkerMap } from "@/lib/validations/layer";

export type OrdinalMarkerSelectorProps = {
  onCustomApply?: (markerMaps: MarkerMap) => void;
  setIsClickAwayEnabled?: (isClickAwayEnabled: boolean) => void;
  onCancel?: () => void;
  label?: string;
  tooltip?: string;
  activeLayerId: string;
  activeLayerField: LayerFieldType;
  markerMaps: MarkerMap;
};

export type MarkerItem = {
  id: string;
  marker: Marker;
};

export type ValueItem = {
  id: string;
  values: string[] | null;
};

export type MarkerMapItem = MarkerItem & {
  value: string[] | null;
};
