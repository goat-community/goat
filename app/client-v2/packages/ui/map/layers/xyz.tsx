import React from "react";
import { Layer, Source } from "react-map-gl";

export type XYZProps = {
  layer: object;
};

export default function XYZLayer(inputProps: XYZProps) {
  const { layer } = inputProps;

  return (
    <Source id={layer.id} type="raster" tiles={[layer.url]}>
      <Layer type="raster" id={layer.id} source={layer.id} />
    </Source>
  );
}
