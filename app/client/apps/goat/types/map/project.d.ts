import type { SourceProps, LayerProps } from "@/types/map/layers";

export interface GroupSharedWith {
  group_id: number;
  group_name: string;
  image_url: string;
}

export interface MapViewState {
  latitude: number;
  longitude: number;
  zoom: number;
  min_zoom: number;
  max_zoom: number;
  bearing: number;
  pitch: number;
}
export interface Report {
  id: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  layers: (SourceProps & LayerProps)[];
  tags: string[];
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  shared_with: GroupSharedWith[];
  initial_view_state: MapViewState;
  reports: Report[];
}
