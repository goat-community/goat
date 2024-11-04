import { Layer, Source } from "react-map-gl/maplibre";

type MaskLayerProps = {
  maskLayerUrl: string;
  maskLayerColor?: string;
  id: string;
  beforeId?: string;
};

const MaskLayer = (props: MaskLayerProps) => {
  return (
    <>
      {/* MASK LAYER  (Shows where tool computation is available*/}
      <Source type="geojson" data={props.maskLayerUrl}>
        <Layer
          id={props.id}
          type="fill"
          beforeId={props.beforeId}
          paint={{
            "fill-color": props.maskLayerColor || "#808080",
            "fill-opacity": 0.8,
          }}
        />
      </Source>
    </>
  );
};

export default MaskLayer;
