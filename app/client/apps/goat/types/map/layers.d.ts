import type { DataType } from "@/types/map/common";


export type SourceProps = {
  data_type: DataType;
  url: string;
  data_source_name: string;
  data_reference_year: number;
};

export type LayerProps = {
  id: string;
  name: string;
  group: string;
  description: string;
  type: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
  active: boolean;
  style: LayerSpecification;
};

interface GroupedLayer {
  url: string;
  data_type: string;
  data_source_name: string;
  data_reference_year: number;
  layers: LayerProps[];
}

export type MapboxOverlayProps = {
  layers: (SourceProps & LayerProps)[];
};
