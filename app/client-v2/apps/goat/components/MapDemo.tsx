import "mapbox-gl/dist/mapbox-gl.css";
import React, { useEffect, useState } from "react";
import ReactMapGL, { Layer, Source } from "react-map-gl";
import { useSelector } from "react-redux";

const MAPBOX_TOKEN =
  "pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA";

export default function MapDemo() {
  const { demoJson } = useSelector((state) => state.mapReducer);

  const [layers, setLayers] = useState([]);

  useEffect(() => {
    if (demoJson) {
      const fetchLayers = async () => {
        const layerPromises = demoJson.layers.map(async (layer) => {
          const styleResponse = await fetch(layer.style);
          const styleJson = await styleResponse.json();
          return {
            ...layer,
            style: styleJson,
          };
        });
        const resolvedLayers = await Promise.all(layerPromises);

        setLayers(resolvedLayers);
      };

      fetchLayers();
    }
  }, [demoJson]);

  return (
    <div className="map-wrap">
      <ReactMapGL
        initialViewState={{
          longitude: demoJson.initial_view_state.longitude,
          latitude: demoJson.initial_view_state.latitude,
          zoom: demoJson.initial_view_state.zoom,
          bearing: demoJson.initial_view_state.bearing,
          pitch: demoJson.initial_view_state.pitch,
        }}
        style={{ width: "100%", height: "100%" }}
        // mapStyle="https://api.maptiler.com/maps/topo-v2/style.json?key=169weMz7cpAoQfwWeK8n"
        mapStyle="mapbox://styles/mapbox/streets-v11"
        mapboxAccessToken={MAPBOX_TOKEN}>
        {layers.map((layer) => (
          <Source key={layer.id} id={layer.id} type="vector" tiles={[layer.url]}>
            {/*<Source key={layer.id} id={layer.id} type="vector" url={layer.style.sources.composite.url}>*/}
            <Layer {...layer.style.layers[0]} />
          </Source>
        ))}
      </ReactMapGL>
    </div>
  );
}
