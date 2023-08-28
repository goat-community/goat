import React from "react";
import { Layer, Source } from "react-map-gl";

export type WMSProps = {
  layer: object;
};

export default function WMSLayer(inputProps: WMSProps) {
  const { layer } = inputProps;
  return (
    <Source id={layer.id} type="raster" tiles={[layer.url]} tileSize={256}>
      <Layer type="raster" id={layer.id} source={layer.id} />
    </Source>
  );
}
