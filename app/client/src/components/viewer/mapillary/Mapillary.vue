<template>
  <div id="mapillary-container">
    <mapillary-image-preview
      ref="imagePreview"
      :imageUrl="previewImageUrl"
      v-show="previewImageUrl.length > 1"
    />
  </div>
</template>
<script>
import { Viewer } from "mapillary-js";

//Ol imports
import OlVectorLayer from "ol/layer/Vector";
import OlVectorSource from "ol/source/Vector";
import OlPoint from "ol/geom/Point";
import OlVectorTileLayer from "ol/layer/VectorTile";
import OlVectorTileSource from "ol/source/VectorTile";
import OlOverlay from "ol/Overlay";
import { createXYZ } from "ol/tilegrid";
import { fromLonLat } from "ol/proj";
import OlFeature from "ol/Feature";
import MVT from "ol/format/MVT";
import { unByKey } from "ol/Observable";

//Style and map object import
import { mapillaryStyleDefs } from "../../../style/OlStyleDefs";
import { Mapable } from "../../../mixins/Mapable";

// Image preview component import (enabled on hover)
import MapillaryImagePreview from "./controls/MapillaryImagePreview";

import "mapillary-js/dist/mapillary.min.css";

export default {
  name: "app-mapillary",
  components: {
    "mapillary-image-preview": MapillaryImagePreview
  },
  props: {
    clientId: {
      type: String,
      required: false,
      default: "V1Qtd0JKNGhhb1J1cktMbmhFSi1iQTo5ODMxOWU3NmZlMjEyYTA3"
    },
    startImageKey: {
      type: String,
      required: false,
      default: "rrKZdmgdvup_KYJKTESq0Q"
    },
    organization_key: {
      type: String,
      required: false,
      default: "RmTboeISWnkEaYaSdtVRHp"
    },
    startSequenceKey: {
      type: String,
      required: false,
      default: "k09tczrhxcsphcmlbo0dt2"
    },
    baseLayerExtent: {
      type: Array,
      required: false
    }
  },
  data() {
    return {
      // Keys
      baseOverlayUrl:
        "https://d25uarhxywzl1j.cloudfront.net/v0.1/{z}/{x}/{y}.mvt",
      // Preview Image url
      previewImageUrl: "",
      // Mapillary viewer
      mapillary: null,
      // Features
      highlightFeature: null,
      pointFeature: null,
      // Layers
      movePointLayer: null,
      baseOverlayerLayer: null,
      hoverHighlightLayer: null,
      // Listener keys
      mapClickListenerKey: null,
      mapHoverListenerKey: null,
      // Overlays
      imagePreviewOverlay: null
    };
  },
  mixins: [Mapable],
  mounted() {
    this.mapillary = new Viewer(
      "mapillary-container",
      this.clientId,
      this.startImageKey,
      {
        component: { cover: false }
      }
    );

    window.addEventListener("resize", this.resize());
    this.createFeatureOverlay();
    this.createImagePreviewOverlay();
    this.createMovePointLayer();
    this.createBaseOverlayLayer();
    this.createHoverHighlightLayer();
    this.addInteractions();
    this.mapClickListenerKey = this.map.on("click", this.onClick);
    this.mapillary.on(Viewer.nodechanged, this.mapillaryChanged);
    mapillaryStyleDefs.activeSequence = this.startSequenceKey;
  },
  methods: {
    /**
     * Overlay style
     */
    createFeatureOverlay() {
      this.featureOverlay = new OlVectorLayer({
        source: new OlVectorSource(),
        map: this.map,
        style: [
          mapillaryStyleDefs.wifiStyle,
          mapillaryStyleDefs.circleSolidStyle
        ]
      });
    },

    /**
     * Image preview overlay
     */

    /**
     * Show popup for the get info module.
     */
    createImagePreviewOverlay() {
      this.imagePreviewOverlay = new OlOverlay({
        element: this.$refs.imagePreview.$el,
        autoPan: false,
        autoPanMargin: 40,
        autoPanAnimation: {
          duration: 250
        }
      });
      this.map.addOverlay(this.imagePreviewOverlay);
    },

    /**
     * Radar point layer
     */
    createMovePointLayer() {
      this.pointFeature = new OlFeature({
        geometry: null
      });
      this.pointFeature.setStyle([
        mapillaryStyleDefs.wifiStyle,
        mapillaryStyleDefs.circleSolidStyle
      ]);
      this.movePointLayer = new OlVectorLayer({
        zIndex: 10,
        source: new OlVectorSource({ features: [this.pointFeature] })
      });
      this.map.addLayer(this.movePointLayer);
    },

    /**
     * Overlay layer (sequences, images)
     */
    createBaseOverlayLayer() {
      this.baseOverlayerLayer = new OlVectorTileLayer({
        name: "mapillaryBaseOverlay",
        source: new OlVectorTileSource({
          attributions: "© Mapillary",
          format: new MVT(),
          tileGrid: createXYZ({ maxZoom: 14 }),
          tilePixelRatio: 16,
          opacity: 0.7,
          url: this.baseOverlayUrl,
          tileLoadFunction: function(tile, url) {
            tile.setLoader(function(extent, resolution, projection) {
              fetch(url).then(function(response) {
                response.arrayBuffer().then(function(data) {
                  const format = tile.getFormat(); // ol/format/MVT configured as source format
                  let features = format.readFeatures(data, {
                    extent: extent,
                    featureProjection: projection
                  });
                  tile.setFeatures(features);
                });
              });
            });
          }
        }),
        style: mapillaryStyleDefs.baseOverlayStyle(this.map)
      });
      if (this.baseLayerExtent) {
        this.baseOverlayerLayer.setExtent(this.baseLayerExtent);
      }
      this.map.addLayer(this.baseOverlayerLayer);
    },

    /**
     * Create hover highlight layers
     */
    createHoverHighlightLayer() {
      this.hoverHighlightLayer = new OlVectorLayer({
        zIndex: 20,
        name: "mapillaryHighlightLayer",
        source: new OlVectorSource(),
        style: mapillaryStyleDefs.highlightStyle
      });
      this.map.addLayer(this.hoverHighlightLayer);
    },

    /**
     * Overlay layer interactions
     */
    addInteractions() {
      this.mapHoverListenerKey = this.map.on("pointermove", evt => {
        let features = this.map.getFeaturesAtPixel(evt.pixel, {
          layerFilter: candidate => {
            if (candidate.get("name") === "mapillaryBaseOverlay") {
              return true;
            }
            return false;
          }
        });
        this.hoverHighlightLayer.getSource().clear();
        if (
          features.length > 0 &&
          features[0].getProperties().layer === "mapillary-images"
        ) {
          this.previewImageUrl = `https://images.mapillary.com/${features[0].get(
            "key"
          )}/thumb-320.jpg`;
          this.imagePreviewOverlay.setPosition(
            features[0].getFlatCoordinates()
          );
          const feature = new OlFeature({
            geometry: new OlPoint(features[0].getFlatCoordinates())
          });
          feature.setProperties(features[0].getProperties());
          this.hoverHighlightLayer.getSource().addFeature(feature);
          this.map.getTarget().style.cursor = "pointer";
        } else {
          this.previewImageUrl = "";
          this.imagePreviewOverlay.setPosition(undefined);
          this.map.getTarget().style.cursor = "";
        }
      });
    },

    /**
     * Click event handler
     */
    onClick(evt) {
      this.hoverHighlightLayer.getSource().clear();
      const feature = this.map.forEachFeatureAtPixel(
        evt.pixel,
        function(feature) {
          return feature;
        },
        {
          layerFilter: layer => {
            return layer === this.baseOverlayerLayer;
          },
          hitTolerance: 5
        }
      );

      if (feature) {
        if (feature.get("layer") === "mapillary-sequences") {
          return;
        }
        var bearing = feature.get("ca");
        this.mapillary.moveToKey(feature.get("key"));
        this.featureOverlay.setStyle(
          mapillaryStyleDefs.updateBearingStyle(bearing)
        );
        mapillaryStyleDefs.activeSequence = feature.get("skey");
      } else {
        return;
      }
      //Update layer
      this.baseOverlayerLayer.changed();
    },

    /**
     * Mapillary changed event handler
     */
    mapillaryChanged(node) {
      if (this.featureOverlay.getVisible()) {
        this.featureOverlay.setVisible(false);
      }
      const lonLat = new fromLonLat([
        node.originalLatLon.lon,
        node.originalLatLon.lat
      ]);
      this.map.getView().animate({
        center: lonLat,
        duration: 400
      });
      if (this.pointFeature.getGeometry() === null) {
        this.pointFeature.setGeometry(new OlPoint(lonLat));
      } else {
        this.pointFeature.getGeometry().setCoordinates(lonLat);
      }
      this.pointFeature.setStyle(
        mapillaryStyleDefs.updateBearingStyle(node.ca)
      );
    },

    /**
     * Resize method
     */
    resize() {
      this.mapillary.resize();
    }
  },
  destroyed() {
    unByKey(this.mapClickListenerKey);
    unByKey(this.mapHoverListenerKey);
    this.map.removeLayer(this.movePointLayer);
    this.map.removeLayer(this.baseOverlayerLayer);
    this.map.removeLayer(this.hoverHighlightLayer);
    this.map.removeOverlay(this.imagePreviewOverlay);
    window.removeEventListener("resize", this.resize());
    this.mapillary.off(Viewer.nodechanged, this.mapillaryChanged);
    this.mapillary.getComponent("sequence").stop();
  }
};
</script>
<style lang="css" scoped></style>
