import maplibregl from "maplibre-gl";
import type { Map } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useRef, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

export default function CustomMap() {
  const { test } = useSelector((state) => state.mapReducer);

  const [lng] = useState(11.537192290815145);
  const [lat] = useState((48.27059464660387 + 48.03915718648435) / 2);
  const [zoom] = useState(10);
  const [API_KEY] = useState("169weMz7cpAoQfwWeK8n");

  const [geojson, setGeojson] = useState(null);

  console.log("test", test);

  const mapContainer = useRef(null);
  const map = useRef<Map>(null);

  const dispatch = useDispatch();

  useEffect(() => {
    if (map.current) return;

    if (geojson) {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: "https://api.maptiler.com/maps/topo-v2/style.json?key=169weMz7cpAoQfwWeK8n",
        center: [lng, lat],
        zoom: zoom,
      }) as Map;

      if (map.current != null) {
        map.current.addControl(new maplibregl.NavigationControl(), "top-right");

        map.current.on("load", function () {
          map.current.addSource("geojson", {
            type: "geojson",
            data: geojson,
          });

          map.current.addLayer({
            id: "geojson",
            type: "fill",
            source: "geojson",
            paint: {
              "fill-color": "gray",
              "fill-opacity": 0.3,
            },
          });
        });
      }
    }
  }, [API_KEY, lng, lat, zoom, geojson]);

  useEffect(() => {
    fetch("https://goat-dev.plan4better.de/api/v1/users/me/study-area", {
      headers: {
        Authorization:
          "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODk0MDE2MTQsInN1YiI6IjU2NSIsInNjb3BlcyI6W119.XllLvUiRHb3r2qTLUgp4Tn2_3ZljLzYpoWaxg_XMNqw",
      },
    })
      .then((res) => res.json())
      .then((json) => {
        setGeojson(json);
      });

    fetch("https://goat-dev.plan4better.de/api/v1/customizations/me", {
      headers: {
        Authorization:
          "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODk0MDE2MTQsInN1YiI6IjU2NSIsInNjb3BlcyI6W119.XllLvUiRHb3r2qTLUgp4Tn2_3ZljLzYpoWaxg_XMNqw",
      },
    });

    fetch(
      "https://api.mapbox.com/styles/v1/mapbox/streets-v10?access_token=pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA"
    ).then((res) => res.json());
  }, []);

  return (
    <div className="map-wrap">
      <div ref={mapContainer} className="map" />
    </div>
  );
}
