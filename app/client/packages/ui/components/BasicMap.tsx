import "mapbox-gl/dist/mapbox-gl.css";
import React from "react";
import Map, { ScaleControl, NavigationControl } from "react-map-gl";

export type MapProps = {
  MAP_ACCESS_TOKEN: string;
  initialViewState: {
    altitude: number;
    bearing: number;
    latitude: number;
    zoom: number;
    pitch: number;
    longitude: number;
  };
  mapStyle: string;
  scaleShow: boolean;
  navigationControl: boolean;
};

export default function BasicMap(props: MapProps) {
  const { initialViewState, MAP_ACCESS_TOKEN, mapStyle, scaleShow, navigationControl } = props;

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <Map
        initialViewState={initialViewState}
        style={{ width: "100%", height: "100%" }}
        mapStyle={mapStyle}
        mapboxAccessToken={MAP_ACCESS_TOKEN}>
        {scaleShow && <ScaleControl />}
        {navigationControl && <NavigationControl />}
      </Map>
    </div>
  );
}
