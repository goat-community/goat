interface Link {
  href: string;
  rel: string;
  type: string;
}

interface Extent {
  spatial: {
    bbox: [number, number, number, number];
    crs: string;
  };
}

export interface LayerData {
  id: string;
  title: string;
  links: Link[];
  extent: Extent;
  itemType: string;
  crs: string[];
}

type GeoJSONGeometry = {
  type: string;
  coordinates: number[];
};

type KeyProperty = {
  name: string;
  type: string;
};

export type KeyDataType = {
  title: string;
  properties: {
    geom: {
      $ref: string;
    };
    category: UserDataProperty;
    housenumber: UserDataProperty;
    name: UserDataProperty;
    street: UserDataProperty;
    random_float: UserDataProperty;
    random_int: UserDataProperty;
    random_date: UserDataProperty;
    id: UserDataProperty;
  };
  type: string;
  $schema: string;
  $id: string;
};

export interface LayerPropsMode {
  type: "number" | "date" | "string";
  name: string;
}

interface ComparerMode {
  label: string;
  value: string;
  type: "number" | "date" | "text" | "select" | "dual_number" | "none" | "year_filter" | "dualDate";
  select: boolean;
}
