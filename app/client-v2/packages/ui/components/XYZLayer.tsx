import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map, { Layer,  Source } from "react-map-gl";

const MAPBOX_TOKEN =
  "pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA";

const obj = {
  id: "123e4567-e89b-12d3-a456-426614174004",
  name: "Example Image Layer XYZ",
  group: "Example Group 2",
  description: "This is an example for a image layer",
  center: [12, 48],
  zoom: 10,
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
}


export default function XYZLayer() {

  return (
    <div style={{ width: "100%", height: "100vh" }}>
        <Map
          initialViewState={{
            latitude: obj.center[1],
            longitude: obj.center[0],
            zoom: obj.zoom,
          }}
          style={{width: "100%", height: "100%"}}
          mapStyle="mapbox://styles/mapbox/streets-v11"
          mapboxAccessToken={MAPBOX_TOKEN}>
          <Source id={obj.id} type="raster" tiles={[obj.url]}>
            <Layer type="raster" id={obj.id} source={obj.id} />
          </Source>
        </Map>
    </div>
  );
}
