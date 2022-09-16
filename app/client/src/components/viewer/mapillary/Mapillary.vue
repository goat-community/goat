<template>
  <div id="mapillary-container" style="width: 100%; height: 100%;">
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
import { transformExtent } from "ol/proj";
// import { toLonLat } from "ol/proj";
// import axios from "axios";

//Style and map object import
import { mapillaryStyleDefs } from "../../../style/OlStyleDefs";
import { Mapable } from "../../../mixins/Mapable";
import { mapFields } from "vuex-map-fields";

// Image preview component import (enabled on hover)
import MapillaryImagePreview from "./controls/MapillaryImagePreview";

import "mapillary-js/dist/mapillary.css";
import { debounce } from "../../../utils/Helpers";

export default {
  name: "app-mapillary",
  components: {
    "mapillary-image-preview": MapillaryImagePreview
  },
  props: {
    accessToken: {
      type: String,
      required: false,
      default: "MLY|4945732362162775|a3872ee8a2b737be51db110cdcdea3d4"
    },
    baseLayerExtent: {
      type: Array,
      required: false
    }
  },
  data() {
    return {
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
    const container = document.getElementById("mapillary-container");
    const mapCenter = this.map.getView().getCenter();
    const searchBounds = [
      mapCenter[0] - 1500,
      mapCenter[1] - 1500,
      mapCenter[0] + 1500,
      mapCenter[1] + 1500
    ];
    const extent = transformExtent(searchBounds, "EPSG:3857", "EPSG:4326");
    fetch(
      `https://graph.mapillary.com/images?fields=id,sequence&bbox=${extent.toString()}&limit=1`,
      {
        headers: { Authorization: "OAuth " + this.accessToken }
      }
    )
      .then(response => response.json())
      .then(response => {
        this.isMapillaryBtnDisabled = false;
        if (Array.isArray(response.data) && response.data.length > 0) {
          const startImageId = response.data[0].id;
          mapillaryStyleDefs.activeSequence = response.data[0].sequence;
          console.log(response.data[0]);
          this.mapillary = new Viewer({
            accessToken: this.accessToken,
            container: container,
            imageId: startImageId,
            component: { cover: false }
          });
          this.isMapillaryBtnDisabled = false;
          window.addEventListener("resize", this.resize());
          this.createBaseOverlayLayer();
          this.mapillary.on("image", this.mapillaryChanged);
          this.createFeatureOverlay();
          this.createImagePreviewOverlay();
          this.createMovePointLayer();
          this.createHoverHighlightLayer();
          this.addInteractions();
          this.mapClickListenerKey = this.map.on("click", this.onClick);
          this.$nextTick(() => {
            this.resize();
          });
        }
      })
      .catch(() => {
        this.isMapillaryBtnDisabled = false;
      });
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
        renderMode: "image",
        source: new OlVectorTileSource({
          attributions:
            "© <a href='https://www.mapillary.com/'> <img src='./static/layer-styles/assets/icons/_backgroundLayers/mapillary.svg' width='12px' height='12px'> Mapillary</a>",
          format: new MVT(),
          tileGrid: createXYZ({ maxZoom: 14 }),
          tilePixelRatio: 16,
          opacity: 0.7,
          url: `https://tiles.mapillary.com/maps/vtp/mly1_computed_public/2/{z}/{x}/{y}?access_token=${this.accessToken}`
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
    async addInteractions() {
      this.mapHoverListenerKey = this.map.on(
        "pointermove",
        debounce(async evt => {
          let features = this.map.getFeaturesAtPixel(evt.pixel, {
            layerFilter: candidate => {
              if (candidate.get("name") === "mapillaryBaseOverlay") {
                return true;
              }
              return false;
            }
          });
          features = features.filter(feature => {
            return feature.get("layer") === "image";
          });
          this.hoverHighlightLayer.getSource().clear();
          if (features.length > 0 && features[0].get("id")) {
            this.imagePreviewOverlay.setPosition(
              features[0].getFlatCoordinates()
            );
            const feature = new OlFeature({
              geometry: new OlPoint(features[0].getFlatCoordinates())
            });
            feature.setProperties(features[0].getProperties());
            this.hoverHighlightLayer.getSource().addFeature(feature);
            this.map.getTarget().style.cursor = "pointer";
            const imageRequestUrl = `https://graph.mapillary.com/${features[0].get(
              "id"
            )}?fields=id,captured_at,compass_angle,sequence,geometry,thumb_256_url`;
            fetch(imageRequestUrl, {
              headers: { Authorization: "OAuth " + this.accessToken }
            })
              .then(response => response.json())
              .then(response => {
                this.previewImageUrl = response.thumb_256_url;
              });
          } else {
            this.previewImageUrl = "";
            this.imagePreviewOverlay.setPosition(undefined);
            this.map.getTarget().style.cursor = "";
          }
        }, 50)
      );
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
        if (feature.get("layer") === "sequence") {
          return;
        }
        var bearing = feature.get("compass_angle");
        this.mapillary.moveTo(feature.get("id"));
        this.featureOverlay.setStyle(
          mapillaryStyleDefs.updateBearingStyle(bearing)
        );
        mapillaryStyleDefs.activeSequence = feature.get("sequence_id");
      } else {
        return;
      }
      //Update layer
      this.baseOverlayerLayer.changed();
    },

    /**
     * Mapillary changed event handler
     */
    mapillaryChanged(evt) {
      if (this.featureOverlay.getVisible()) {
        this.featureOverlay.setVisible(false);
      }
      const image = evt.image;
      const lonLat = new fromLonLat([image.lngLat.lng, image.lngLat.lat]);
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
        mapillaryStyleDefs.updateBearingStyle(image.compassAngle)
      );
    },

    /**
     * Resize method
     */
    resize() {
      this.mapillary.resize();
    }
  },
  computed: {
    ...mapFields("map", {
      isMapillaryBtnDisabled: "isMapillaryBtnDisabled",
      isMapillaryButtonActive: "isMapillaryButtonActive"
    })
  },
  destroyed() {
    unByKey(this.mapClickListenerKey);
    unByKey(this.mapHoverListenerKey);
    this.map.removeLayer(this.movePointLayer);
    this.map.removeLayer(this.baseOverlayerLayer);
    this.map.removeLayer(this.hoverHighlightLayer);
    this.map.removeOverlay(this.imagePreviewOverlay);
    window.removeEventListener("resize", this.resize());
    this.mapillary.off("position", this.mapillaryChanged);
    this.mapillary.getComponent("sequence").stop();
  }
};
</script>
<style lang="css" scoped></style>
