import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map, { Layer,  Source } from "react-map-gl";

const MAPBOX_TOKEN =
  "pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA";

const wmsObj = {
    id: "123e4567-e89b-12d3-a456-426614174003",
    name: "Example Image Layer",
    center: [11.831704345197693, 48.124458667004006],
    zoom: 10.116890419844134,
    group: "Example Group 2",
    description: "This is an example for an image layer",
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
};


export default function WMSLayer() {

  return (
    <div style={{ width: "100%", height: "100vh" }}>
        <Map
          initialViewState={{
            latitude: wmsObj.center[1],
            longitude: wmsObj.center[0],
            zoom: wmsObj.zoom,
          }}
          style={{width: "100%", height: "100%"}}
          mapStyle="mapbox://styles/mapbox/streets-v11"
          mapboxAccessToken={MAPBOX_TOKEN}>
          <Source id={wmsObj.id} type="raster" tiles={[wmsObj.url]} tileSize={256}>
            <Layer type="raster" id={wmsObj.id} source={wmsObj.id} />
          </Source>
        </Map>
    </div>
  );
}
