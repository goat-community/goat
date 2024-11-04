import MapboxDraw from "@mapbox/mapbox-gl-draw";
import { Box, useTheme } from "@mui/material";
import { useCallback, useMemo } from "react";
import { Map, type MapLayerMouseEvent, type MapRef, type ViewState } from "react-map-gl/maplibre";
import type { ViewStateChangeEvent } from "react-map-gl/maplibre";
import { v4 } from "uuid";

import { PATTERN_IMAGES } from "@/lib/constants/pattern-images";
import { setHighlightedFeature, setPopupInfo } from "@/lib/store/map/slice";
import { addOrUpdateMarkerImages, addPatternImages } from "@/lib/transformers/map-image";
import type { FeatureLayerPointProperties, Layer } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";
import type { ScenarioFeatures } from "@/lib/validations/scenario";

import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import Layers from "@/components/map/Layers";
import ScenarioLayer from "@/components/map/ScenarioLayer";
import ToolboxLayers from "@/components/map/ToolboxLayers";
import MapPopoverEditor from "@/components/map/controls/PopoverEditor";
import MapPopoverInfo from "@/components/map/controls/PopoverInfo";
import DrawControl from "@/components/map/controls/draw/Draw";

interface MapProps {
  mapRef: React.RefObject<MapRef> | null;
  initialViewState?: Partial<ViewState> & {
    bounds?: [number, number, number, number];
    fitBoundsOptions?: {
      offset?: [number, number];
      minZoom?: number;
      maxZoom?: number;
      padding?: number | { top: number; bottom: number; left: number; right: number };
    };
  };
  mapStyle: string;
  layers: ProjectLayer[] | Layer[];
  scenarioFeatures?: ScenarioFeatures;
  onMove?: ((e: ViewStateChangeEvent) => void | undefined) | undefined;
  onMoveEnd?: ((e: ViewStateChangeEvent) => void | undefined) | undefined;
  onClick?: (e: MapLayerMouseEvent) => void;
  onLoad?: () => void;
  dragRotate?: boolean | undefined;
  touchZoomRotate?: boolean | undefined;
  children?: React.ReactNode;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  containerSx?: any;
  isEditor?: boolean;
}

const MapViewer: React.FC<MapProps> = ({
  mapRef,
  initialViewState,
  mapStyle,
  layers,
  scenarioFeatures,
  onMove,
  onMoveEnd,
  onClick,
  onLoad,
  dragRotate = false,
  touchZoomRotate = false,
  children,
  containerSx,
  isEditor,
}) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const isGetInfoActive = useAppSelector((state) => state.map.isMapGetInfoActive);
  const mapCursor = useAppSelector((state) => state.map.mapCursor);
  const highlightedFeature = useAppSelector((state) => state.map.highlightedFeature);
  const popupInfo = useAppSelector((state) => state.map.popupInfo);
  const popupEditor = useAppSelector((state) => state.map.popupEditor);

  const _selectedScenarioEditLayer = useAppSelector((state) => state.map.selectedScenarioLayer);
  const selectedScenarioEditLayer = useMemo(() => {
    return layers?.find((layer) => layer.id === _selectedScenarioEditLayer?.value);
  }, [_selectedScenarioEditLayer, layers]);

  const interactiveLayerIds = useMemo(() => layers?.map((layer) => layer.id.toString()), [layers]);

  const handlePopoverClose = () => {
    dispatch(setPopupInfo(undefined));
    dispatch(setHighlightedFeature(undefined));
  };

  const handleMapClick = (e: MapLayerMouseEvent) => {
    const features = e.features;
    const hiddenProperties = ["layer_id", "id", "h3_3", "h3_6"];
    if (features && features.length > 0 && isGetInfoActive) {
      const feature = features[0];
      dispatch(setHighlightedFeature(feature));
      const layerName = layers?.find((layer) => layer.id == feature.layer.id)?.name;
      let lngLat = [e.lngLat.lng, e.lngLat.lat] as [number, number];
      if (feature.geometry.type === "Point" && feature.geometry.coordinates) {
        lngLat = [feature.geometry.coordinates[0], feature.geometry.coordinates[1]];
      }
      const properties = feature.properties;
      const jsonProperties = {};
      const primitiveProperties = {};

      if (properties) {
        for (const key in properties) {
          if (!hiddenProperties.includes(key)) {
            const value = properties[key];
            try {
              const parsedValue = JSON.parse(value);
              if (typeof parsedValue === "object" && parsedValue !== null) {
                jsonProperties[key] = parsedValue;
              } else {
                throw new Error();
              }
            } catch (error) {
              primitiveProperties[key] = value;
            }
          }
        }
      }
      dispatch(
        setPopupInfo({
          lngLat,
          properties: primitiveProperties,
          jsonProperties: jsonProperties,
          title: layerName ?? "",
          onClose: handlePopoverClose,
        })
      );
    } else {
      setHighlightedFeature(null);
      dispatch(setPopupInfo(undefined));
    }
    if (onClick) {
      onClick(e);
    }
  };

  const handleMapOverImmediate = (e: MapLayerMouseEvent) => {
    // Extract features immediately
    const features = e.features;
    if (mapRef?.current) {
      // This is a hack to change the cursor to a pointer when hovering over a feature
      // It's not recommended to change the state of a component through internal methods
      // However, this is the only way to do it with the current version of react-map-gl
      // See https://github.com/visgl/react-map-gl/issues/579#issuecomment-1275163348
      const map = mapRef.current.getMap();
      if (mapCursor) {
        map.getCanvas().style.cursor = mapCursor;
      } else {
        map.getCanvas().style.cursor = features?.length ? "pointer" : "";
      }
    }
  };

  const handleMapLoad = useCallback(() => {
    if (mapRef?.current) {
      // get all icon layers and add icons to map using addOrUpdateMarkerImages method
      layers?.forEach((layer) => {
        if (layer.type === "feature" && layer.feature_layer_geometry_type === "point") {
          const pointFeatureProperties = layer.properties as FeatureLayerPointProperties;
          addOrUpdateMarkerImages(layer.id, pointFeatureProperties, mapRef.current);
        }
      });

      // load pattern images
      addPatternImages(PATTERN_IMAGES ?? [], mapRef.current);
    }
    onLoad && onLoad();
  }, [layers, mapRef, onLoad]);

  return (
    <Box
      sx={{
        width: "100%",
        ".maplibregl-ctrl .maplibregl-ctrl-logo": {
          display: "none",
        },
        height: `100%`,
        ".maplibregl-popup-content": {
          padding: 0,
          borderRadius: "6px",
          background: theme.palette.background.paper,
        },
        ".maplibregl-popup-anchor-top .maplibregl-popup-tip, .maplibregl-popup-anchor-top-left .maplibregl-popup-tip, .maplibregl-popup-anchor-top-right .maplibregl-popup-tip":
          {
            borderBottomColor: theme.palette.background.paper,
          },
        ".maplibregl-popup-anchor-bottom .maplibregl-popup-tip, .maplibregl-popup-anchor-bottom-right .maplibregl-popup-tip, .maplibregl-popup-anchor-bottom-left .maplibregl-popup-tip":
          {
            borderTopColor: theme.palette.background.paper,
          },
        ".maplibregl-popup-anchor-left .maplibregl-popup-tip": {
          borderRightColor: theme.palette.background.paper,
        },
        ".maplibregl-popup-anchor-right .maplibregl-popup-tip": {
          borderLeftColor: theme.palette.background.paper,
        },
        ...containerSx,
      }}>
      <Map
        id="map"
        ref={mapRef}
        style={{ width: "100%", height: "100%" }}
        initialViewState={initialViewState}
        mapStyle={mapStyle}
        interactiveLayerIds={interactiveLayerIds}
        dragRotate={dragRotate}
        touchZoomRotate={touchZoomRotate}
        onMoveEnd={onMoveEnd}
        onClick={handleMapClick}
        onMouseMove={handleMapOverImmediate}
        onMove={onMove}
        onLoad={handleMapLoad}>
        {isEditor && (
          <DrawControl
            position="top-right"
            displayControlsDefault={false}
            defaultMode={MapboxDraw.constants.modes.SIMPLE_SELECT}
          />
        )}
        <Layers
          layers={layers}
          highlightFeature={highlightedFeature}
          scenarioFeatures={scenarioFeatures}
          selectedScenarioLayer={selectedScenarioEditLayer as ProjectLayer}
        />
        <ScenarioLayer scenarioLayerData={scenarioFeatures} projectLayers={layers as ProjectLayer[]} />
        <ToolboxLayers />
        {popupInfo && <MapPopoverInfo key={highlightedFeature?.id ?? v4()} {...popupInfo} />}
        {popupEditor && isEditor && (
          <MapPopoverEditor
            key={popupEditor.feature?.id || popupEditor.feature?.properties?.id || v4()}
            {...popupEditor}
          />
        )}
      </Map>
      {children}
    </Box>
  );
};

export default MapViewer;
