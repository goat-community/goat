import MapboxDraw from "@mapbox/mapbox-gl-draw";
import { useEffect } from "react";
import type { ControlPosition } from "react-map-gl/maplibre";
import { useControl } from "react-map-gl/maplibre";

import { useDraw } from "@/lib/providers/DrawProvider";

import CircleMode from "./custom-modes/circle";

const constants = MapboxDraw.constants;

export enum CustomDrawModes {
  DRAW_CIRCLE = "draw_circle",
}

type DrawControlProps = ConstructorParameters<typeof MapboxDraw>[0] & {
  position?: ControlPosition;

  onCreate?: (evt: { features: object[] }) => void;
  onUpdate?: (evt: { features: object[]; action: string }) => void;
  onDelete?: (evt: { features: object[] }) => void;
};

// eslint-disable-next-line react/display-name
export const DrawControl = (props: DrawControlProps) => {
  const { setDrawControl } = useDraw();

  const modes = MapboxDraw.modes;
  modes[CustomDrawModes.DRAW_CIRCLE] = CircleMode;

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const drawControl = useControl<MapboxDraw>(
    () => new MapboxDraw(props),
    ({ map }) => {
      props.onCreate && map.on(constants.events.CREATE, props.onCreate);
      props.onUpdate && map.on(constants.events.UPDATE, props.onUpdate);
      props.onDelete && map.on(constants.events.DELETE, props.onDelete);
    },
    ({ map }) => {
      props.onCreate && map.off(constants.events.CREATE, props.onCreate);
      props.onUpdate && map.off(constants.events.UPDATE, props.onUpdate);
      props.onDelete && map.off(constants.events.DELETE, props.onDelete);
    },
    {
      position: props.position,
    }
  );

  useEffect(() => {
    if (drawControl) {
      setDrawControl(drawControl);
    }
  }, [drawControl, setDrawControl]);

  return null;
};

export default DrawControl;
