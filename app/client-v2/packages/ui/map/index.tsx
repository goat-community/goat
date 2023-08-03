import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map from "react-map-gl";

import WMSLayer from "./layers/wms";
import XYZLayer from "./layers/xyz";

const obj = {
  id: "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  name: "My new project",
  description: "My new project description",
  thumbnail_url: "https://assets.plan4better.de/api/thumbnail/1.png",
  tags: ["tag1", "tag2"],
  created_by: "elias.pajares@plan4better.de",
  updated_by: "elias.pajares@plan4better.de",
  created_at: "2021-03-03T09:00:00.000000Z",
  updated_at: "2021-03-03T09:00:00.000000Z",
  shared_with: [
    {
      group_id: 1,
      group_name: "My Group 1",
      image_url: "https://assets.plan4better.de/api/thumbnail/1.png",
    },
    {
      group_id: 2,
      group_name: "My Group 2",
      image_url: "https://assets.plan4better.de/api/thumbnail/2.png",
    },
  ],
  scale_show: false,
  navigation_control: false,
  MAP_ACCESS_TOKEN:
    "pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA",
  map_style: "mapbox://styles/mapbox/streets-v11",
  initial_view_state: {
    latitude: 48.1502132,
    longitude: 11.5696284,
    zoom: 10,
    min_zoom: 0,
    max_zoom: 20,
    bearing: 0,
    pitch: 0,
  },
  reports: [],
  layers: [
    {
      id: "123e4567-e89b-12d3-a456-426614174003",
      name: "Example Image Layer",
      group: "Example Group 2",
      description: "This is an example for a image layer",
      type: "image_layer",
      created_at: "2023-07-11T00:00:00",
      created_by: "example_user",
      updated_at: "2023-07-11T00:00:00",
      updated_by: "example_user",
      active: "True",
      data_source_name: "Example Data Source",
      data_reference_year: 2020,
      url: "https://www.lfu.bayern.de/gdi/wms/laerm/hauptverkehrsstrassen?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.1.1&request=GetMap&srs=EPSG:3857&transparent=true&width=256&height=256&layers=mroadbyln2022,mroadbylden2022&styles=",
      legend_urls: [
        "https://www.lfu.bayern.de/gdi/wms/laerm/hauptverkehrsstrassen?request=GetLegendGraphic&version=1.3.0&format=image/png&layer=mroadbyln&SERVICE=WMS&SLD_VERSION=1.1.0&STYLE=&TRANSPARENT=true",
        "https://www.lfu.bayern.de/gdi/wms/laerm/hauptverkehrsstrassen?request=GetLegendGraphic&version=1.3.0&format=image/png&layer=mroadbyln&SERVICE=WMS&SLD_VERSION=1.1.0&STYLE=&TRANSPARENT=true",
      ],
      data_type: "wms",
    },
    {
      id: "123e4567-e89b-12d3-a456-426614174004",
      name: "Example Image Layer XYZ",
      group: "Example Group 2",
      description: "This is an example for a image layer",
      type: "image_layer",
      created_at: "2023-07-11T00:00:00",
      created_by: "example_user",
      updated_at: "2023-07-11T00:00:00",
      updated_by: "example_user",
      active: "True",
      data_source_name: "Example Data Source",
      data_reference_year: 2020,
      url: "https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=402ce1ca8eb54457bdf65e2b261c5132",
      data_type: "xyz",
    },
  ],
};

export type MapLProps = {
  layer: string;
};

export default function MapL(props: MapLProps) {
  const { layer } = props;

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <Map
        initialViewState={obj.initial_view_state}
        style={{ width: "100%", height: "100%" }}
        mapStyle={obj.map_style}
        mapboxAccessToken={obj.MAP_ACCESS_TOKEN}>
        {obj.layers.map((item, index) => {
          if (layer === item.data_type && item.data_type === "wms") {
            return <WMSLayer layer={item} key={index} />;
          }
          if (layer === item.data_type && item.data_type === "xyz") {
            return <XYZLayer layer={item} key={index} />;
          }
        })}
      </Map>
    </div>
  );
}
