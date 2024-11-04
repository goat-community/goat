import type { MapRef } from "react-map-gl/maplibre";

import type { FeatureLayerPointProperties } from "@/lib/validations/layer";
import type { PatternImage } from "@/lib/constants/pattern-images";

// Image prefix for marker images is needed to avoid
// name conflicts with other images from mapbox basemaps
export const PATTERN_IMAGE_PREFIX = "goat-pattern-";

/**
 * Load image from url and adds or updates the map with the image
 * @param map MapRef
 * @param url string
 * @param marker_name string
 * @param width number
 * @param height number
 * @returns void
 */
export const loadImage = (map: MapRef, url: string, marker_name: string, width?: number, height?: number) => {
  const extension = url.split(".").pop()?.toLowerCase();
  const addOrUpdateImage = (
    image:
      | HTMLImageElement
      | { width: number; height: number; data: Uint8Array | Uint8ClampedArray }
      | ImageData
      | ImageBitmap
  ) => {
    if (map?.hasImage(marker_name)) {
      // We can't use `updateImage` because size of the image can't be changed
      map?.removeImage(marker_name);
    }
    map?.addImage(marker_name, image, { sdf: true });
  };

  if (extension === "svg") {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = url;
    img.onload = () => {
      const pixelRatio = window.devicePixelRatio || 1;
      img.width = width || img.width; // Set the width of the image
      img.height = height || img.height; // Set the height of the image
      const canvas = document.createElement("canvas");
      canvas.width = img.width * pixelRatio;
      canvas.height = img.height * pixelRatio;
      const context = canvas.getContext("2d");
      if (context) {
        context.scale(pixelRatio, pixelRatio);
        context.imageSmoothingEnabled = false;
        context.drawImage(img, 0, 0, img.width, img.height);
        addOrUpdateImage({
          width: canvas.width,
          height: canvas.height,
          data: new Uint8Array(context.getImageData(0, 0, canvas.width, canvas.height).data.buffer),
        });
      }
    };
  } else if (extension === "png") {
    map?.loadImage(url).then((image) => {
      addOrUpdateImage(image.data);
    }).catch((error) => {
      console.error(error);
    });
  } else {
    console.error("Unsupported image format");
  }
};

/**
 * Add or update marker images on the map
 * @param properties FeatureLayerPointProperties
 * @param map MapRef
 * @returns void
 */
export function addOrUpdateMarkerImages(id: number, properties: FeatureLayerPointProperties, map: MapRef | null) {
  if (map && properties.custom_marker) {
    const markers = [properties.marker];
    const size = properties.marker_size;
    properties.marker_mapping?.forEach((markerMap) => {
      if (markerMap && markerMap[1]) markers.push(markerMap[1]);
    });
    markers.forEach((marker) => {
      if (marker && marker.url && marker.name) {
        const name = `${id}-${marker.name}`;
        loadImage(map, marker.url, name, size, size);
      }
    });
  }
}


/**
 * Add pattern images on the map
 * @param patterns PatternImage[]
 * @param map MapRef
 */
export function addPatternImages(patterns: PatternImage[], map: MapRef | null) {
  if (map && patterns) {
    patterns.forEach((pattern) => {
      const name = `${PATTERN_IMAGE_PREFIX}${pattern.name}`;
      loadImage(map, pattern.url, name, pattern.width, pattern.height);
    });
  }
}
