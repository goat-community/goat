<template>
  <div id="ol-map-container">
    <!-- Map Controls -->
    <zoom-control
      v-show="!miniViewOlMap"
      :map="map"
      :color="activeColor.primary"
    />
    <full-screen v-show="!miniViewOlMap" :color="activeColor.primary" />
    <progress-status :isNetworkBusy="isNetworkBusy" />
    <background-switcher v-show="!miniViewOlMap" />
    <map-legend v-show="!miniViewOlMap" :color="activeColor.primary" />
    <!-- Popup overlay  -->
    <overlay-popup
      :color="activeColor.primary"
      :title="popup.title"
      v-show="popup.isVisible && miniViewOlMap === false"
      ref="popup"
    >
      <v-btn icon>
        <v-icon>close</v-icon>
      </v-btn>
      <template v-slot:close>
        <template v-if="getInfoResult.length > 1">
          <span
            >({{ popup.currentLayerIndex + 1 }} of
            {{ getInfoResult.length }})</span
          >
          <v-icon
            :disabled="popup.currentLayerIndex === 0"
            style="cursor:pointer;"
            @click="previousGetInfoLayer()"
            >chevron_left</v-icon
          >
          <v-icon
            :disabled="popup.currentLayerIndex === getInfoResult.length - 1"
            style="cursor:pointer;"
            @click="nextGetInfoLayer()"
            >chevron_right</v-icon
          >
        </template>
        <v-btn @click="closePopup()" icon>
          <v-icon>close</v-icon>
        </v-btn>
      </template>
      <template v-slot:body>
        <div class="subtitle-2 mb-4 font-weight-bold">
          {{ getPopupTitle() }}
        </div>

        <a
          v-if="currentInfoFeature && currentInfoFeature.get('osm_id')"
          style="text-decoration:none;"
          :href="getOsmHrefLink()"
          target="_blank"
          title=""
        >
          <i class="fa fa-edit"></i> {{ $t("map.popup.editWithOsm") }}</a
        >

        <v-divider></v-divider>

        <div style="height:190px;">
          <vue-scroll>
            <v-simple-table dense class="pr-2">
              <template v-slot:default>
                <tbody>
                  <tr v-for="item in currentInfo" :key="item.property">
                    <td>{{ item.property }}</td>
                    <td>{{ item.value }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </vue-scroll>
        </div>

        <v-divider></v-divider>
      </template>
    </overlay-popup>
  </div>
</template>

<script>
import Vue from "vue";
import Map from "ol/Map";
import View from "ol/View";

// ol imports
import Overlay from "ol/Overlay";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import Mask from "ol-ext/filter/Mask";
import OlFill from "ol/style/Fill";

// style imports
import { getInfoStyle } from "../../../style/OlStyleDefs";
// import the app-wide EventBus
import { EventBus } from "../../../EventBus";

// utils imports
import { LayerFactory } from "../../../factory/layer.js";
import { groupBy, humanize, isCssColor } from "../../../utils/Helpers";
import { getAllChildLayers, getLayerType } from "../../../utils/Layer";
import { geojsonToFeature } from "../../../utils/MapUtils";
import { Group as LayerGroup } from "ol/layer.js";
import http from "../../../services/http";
import axios from "axios";

//Store imports
import { mapMutations, mapGetters, mapActions } from "vuex";

//Map Controls
import OverlayPopup from "./controls/Overlay";
import MapLoadingProgressStatus from "./controls/MapLoadingProgressStatus";
import Legend from "./controls/Legend";
import BackgroundSwitcher from "./controls/BackgroundSwitcher";
import ZoomControl from "./controls/ZoomControl";
import FullScreen from "./controls/Fullscreen";
import DoubleClickZoom from "ol/interaction/DoubleClickZoom";

import { defaults as defaultControls, Attribution } from "ol/control";
import { defaults as defaultInteractions } from "ol/interaction";

// Context menu
import ContextMenu from "ol-contextmenu/dist/ol-contextmenu";
import "ol-contextmenu/dist/ol-contextmenu.min.css";

export default {
  components: {
    "overlay-popup": OverlayPopup,
    "progress-status": MapLoadingProgressStatus,
    "map-legend": Legend,
    "background-switcher": BackgroundSwitcher,
    "zoom-control": ZoomControl,
    "full-screen": FullScreen
  },
  name: "app-ol-map",
  props: {
    miniViewOlMap: { type: Boolean, required: true }
  },
  data() {
    return {
      zoom: this.$appConfig.map.zoom,
      center: this.$appConfig.map.center,
      minZoom: this.$appConfig.map.minZoom,
      maxZoom: this.$appConfig.map.maxZoom,
      extent: this.$appConfig.map.extent, // Extent is fetched dynamically from the study area
      color: this.$appConfig.controlsColor,
      allLayers: [],
      queryableLayers: [],
      activeInteractions: [],
      popup: {
        rawHtml: null,
        title: "info",
        isVisible: false,
        currentLayerIndex: 0
      },
      getInfoResult: []
    };
  },
  mounted() {
    var me = this;
    // Make the OL map accessible for Mapable mixin even 'ol-map-mounted' has
    // already been fired. Don not use directly in cmps, use Mapable instead.
    Vue.prototype.$map = me.map;
    // Send the event 'ol-map-mounted' with the OL map as payload
    EventBus.$emit("ol-map-mounted", me.map);
    //Add map to the vuex store.
    me.setMap(me.map);
    // resize the map, so it fits to parent
    window.setTimeout(() => {
      me.map.setTarget(document.getElementById("ol-map-container"));
      me.map.updateSize();

      // adjust the bg color of the OL buttons (like zoom, rotate north, ...)
      me.setOlButtonColor();

      me.setupMapHover();

      //Get Info
      me.setupMapClick();
      me.setupMapPointerMove();
      me.createPopupOverlay();
    }, 200);
  },
  created() {
    var me = this;

    // Make map rotateable according to property
    const attribution = new Attribution({
      collapsible: true
    });

    //Need to reference as we should deactive double click zoom when there
    //are active interaction like draw/modify
    this.dblClickZoomInteraction = new DoubleClickZoom();
    me.map = new Map({
      layers: [],
      interactions: defaultInteractions({
        altShiftDragRotate: me.rotateableMap,
        doubleClickZoom: false
      }).extend([this.dblClickZoomInteraction]),
      controls: defaultControls({
        attribution: false,
        zoom: false
      }).extend([attribution]),
      view: new View({
        center: me.center || [0, 0],
        zoom: me.zoom,
        extent: me.extent,
        minZoom: me.minZoom,
        maxZoom: me.maxZoom
      })
    });

    // Create layers from config and add them to map
    const layers = me.createLayers();
    me.map.getLayers().extend(layers);
    me.createMaskFilters(layers);
    me.createGetInfoLayer();

    // Setup context menu (right-click)
    me.setupContentMenu();

    // Event bus setup for managing interactions
    EventBus.$on("ol-interaction-activated", startedInteraction => {
      me.activeInteractions.push(startedInteraction);
    });
    EventBus.$on("ol-interaction-stoped", stopedInteraction => {
      me.activeInteractions = Array.from(new Set(me.activeInteractions));
      me.activeInteractions = me.activeInteractions.filter(interaction => {
        return interaction !== stopedInteraction;
      });
    });
    EventBus.$on("close-popup", () => {
      me.closePopup();
    });
  },

  methods: {
    /**
     * Creates the OL layers due to the map "layers" array in app config.
     * @return {ol.layer.Base[]} Array of OL layer instances
     */
    createLayers() {
      let layers = [];
      const me = this;
      const layersConfigGrouped = groupBy(this.$appConfig.map.layers, "group");
      for (var group in layersConfigGrouped) {
        if (!layersConfigGrouped.hasOwnProperty(group)) {
          continue;
        }
        const mapLayers = [];
        layersConfigGrouped[group].reverse().forEach(function(lConf) {
          const layer = LayerFactory.getInstance(lConf);
          mapLayers.push(layer);
          if (layer.get("name")) {
            me.setLayer(layer);
          }
        });
        let layerGroup = new LayerGroup({
          name: group !== undefined ? group.toString() : "Other Layers",
          layers: mapLayers
        });
        layers.push(layerGroup);
      }

      return layers;
    },

    /**
     * Creates a layer to visualize selected GetInfo features.
     */
    createGetInfoLayer() {
      const source = new VectorSource({
        wrapX: false
      });
      const vector = new VectorLayer({
        name: "Get Info Layer",
        displayInLayerList: false,
        zIndex: 100,
        source: source,
        style: getInfoStyle()
      });
      this.getInfoLayerSource = source;
      this.map.addLayer(vector);
    },

    /**
     * Map hover used for helper tooltips.
     */
    setupMapHover() {
      const me = this;
      const map = me.map;

      //Adds map helptooltip overlay
      let helptooltipOverlayEl = document.createElement("div");
      let helptooltipCurrentMessage = me.helpTooltip.currentMessage;
      helptooltipOverlayEl.className = "tooltip tooltip-help";
      let helptooltipOverlay = new Overlay({
        element: helptooltipOverlayEl,
        offset: [15, 15],
        positioning: "top-left"
      });
      helptooltipOverlay.setPosition(undefined);
      helptooltipOverlayEl.innerHTML = helptooltipCurrentMessage;
      map.addOverlay(helptooltipOverlay);

      //Init map hover event

      map.on("pointermove", function(event) {
        //Check helptooltip status
        if (me.helpTooltip.isActive) {
          helptooltipOverlay.setPosition(event.coordinate);
          if (me.helpTooltip.currentMessage !== helptooltipCurrentMessage) {
            helptooltipOverlayEl.innerHTML = me.helpTooltip.currentMessage;
            helptooltipCurrentMessage = me.helpTooltip.currentMessage;
          }
        } else {
          if (helptooltipOverlay.getPosition() !== undefined) {
            helptooltipOverlay.setPosition(undefined);
          }
        }
      });
    },

    /**
     * Creates a filter mask of the city using ol mask extension.
     * Hides other municipalities and states.
     */
    createMaskFilters(mapLayers) {
      //Filter background layers
      const backgroundLayers = [];
      mapLayers.forEach(layer => {
        if (layer.get("name") === "backgroundLayers") {
          backgroundLayers.push(...layer.getLayers().getArray());
        }
      });

      //Create masks
      const feature = this.$appConfig.map.studyAreaFeature;

      if (!feature[0]) return;
      const mask = new Mask({
        feature: feature[0],
        inner: false,
        fill: new OlFill({ color: [169, 169, 169, 0.8] })
      });
      for (const i of backgroundLayers) {
        i.addFilter(mask);
      }
    },

    /**
     * Sets the background color of the OL buttons to the color property.
     */
    setOlButtonColor() {
      var me = this;

      if (isCssColor(me.activeColor.primary)) {
        // directly apply the given CSS color
        const rotateEl = document.querySelector(".ol-rotate");
        if (rotateEl) {
          rotateEl.className += " elevation-5";
          rotateEl.borderRadius = "40px";
          const rotateElStyle = document.querySelector(
            ".ol-rotate .ol-rotate-reset"
          ).style;
          rotateElStyle.backgroundColor = me.activeColor.primary;
          rotateElStyle.borderRadius = "40px";
        }
        const attrEl = document.querySelector(".ol-attribution");
        if (attrEl) {
          attrEl.className += " elevation-5";
          const elStyle = document.querySelector(
            ".ol-attribution button[type='button']"
          ).style;
          elStyle.backgroundColor = me.activeColor.primary;
          elStyle.borderRadius = "40px";
        }
      } else {
        // apply vuetify color by transforming the color to the corresponding
        // CSS class (see https://vuetifyjs.com/en/framework/colors)
        const [colorName, colorModifier] = me.activeColor.primary
          .toString()
          .trim()
          .split(" ", 2);

        if (document.querySelector(".ol-rotate")) {
          document
            .querySelector(".ol-rotate .ol-rotate-reset")
            .classList.add(colorName);
          document
            .querySelector(".ol-rotate .ol-rotate-reset")
            .classList.add(colorModifier);
        }
      }
    },

    /**
     * Show popup for the get info module.
     */
    createPopupOverlay() {
      const me = this;
      me.popupOverlay = new Overlay({
        element: me.$refs.popup.$el,
        autoPan: false,
        autoPanMargin: 40,
        autoPanAnimation: {
          duration: 250
        }
      });
      me.map.addOverlay(me.popupOverlay);
    },

    /**
     * Closes the popup if user click X button.
     */
    closePopup() {
      const me = this;
      if (me.popupOverlay) {
        me.popupOverlay.setPosition(undefined);
        me.popup.isVisible = false;
      }
      me.getInfoResult = [];
      me.popup.currentLayerIndex = 0;
      if (me.getInfoLayerSource) {
        me.getInfoLayerSource.clear();
      }
    },

    /**
     * Show getInfo popup.
     */
    showPopup() {
      // Clear highligh feature
      this.getInfoLayerSource.clear();
      let position = this.getInfoResult[this.popup.currentLayerIndex]
        .getGeometry()
        .getCoordinates();
      // Add highlight feature
      this.getInfoLayerSource.addFeature(
        this.getInfoResult[this.popup.currentLayerIndex]
      );
      while (position && Array.isArray(position[0])) {
        position = position[0];
      }
      this.map.getView().animate({
        center: position,
        duration: 400
      });
      this.popupOverlay.setPosition(position);
      this.popup.isVisible = true;
      this.popup.title = `info`;
    },

    /**
     * Map pointer move event .
     */
    setupMapPointerMove() {
      this.mapPointerMoveListenerKey = this.map.on("pointermove", evt => {
        if (
          evt.dragging ||
          this.activeInteractions.length > 0 ||
          !this.isochroneLayer
        ) {
          return;
        }
        const features = this.map.getFeaturesAtPixel(evt.pixel, {
          layerFilter: candidate => {
            if (candidate.get("name") === "Isochrone Layer") {
              return true;
            }
            return false;
          }
        });

        this.map.getTarget().style.cursor =
          features.length > 0 ? "pointer" : "";
      });
    },

    /**
     * Right click menu .
     */
    setupContentMenu() {
      const contextMenu = new ContextMenu({
        width: 170,
        defaultItems: true // defaultItems are (for now) Zoom In/Zoom Out
      });

      // Rename default items
      for (let item of contextMenu.getDefaultItems()) {
        if (item.text === "Zoom In") {
          item.text = this.$t("map.contextMenu.zoomIn");
          item.label = "zoomIn";
        } else if (item.text === "Zoom Out") {
          item.text = this.$t("map.contextMenu.zoomOut");
          item.label = "zoomOut";
        }
      }

      this.setContextMenu(contextMenu);
      this.map.addControl(contextMenu);

      // Before open event
      contextMenu.on("beforeopen", () => {
        let defaultItems = contextMenu.getDefaultItems();
        defaultItems.forEach(defaultItem => {
          defaultItem.text = this.$t(`map.contextMenu.${defaultItem.label}`);
        });
        contextMenu.clear();
        contextMenu.extend(defaultItems);
      });
    },

    /**
     * Map click event for Module.
     */
    setupMapClick() {
      const me = this;
      const map = me.map;
      me.mapClickListenerKey = map.on("click", evt => {
        me.closePopup();
        if (me.activeInteractions.length > 0) {
          return;
        }

        //Check for isochrone features
        const features = me.map.getFeaturesAtPixel(evt.pixel, {
          layerFilter: candidate => {
            if (candidate.get("name") === "Isochrone Layer") {
              return true;
            }
            return false;
          }
        });
        if (features.length > 0) {
          // Toggle thematic data for isochrone window
          const isochroneFeature = features[0];
          this.showIsochroneWindow({
            id: isochroneFeature.get("calculationNumber"),
            calculationType: isochroneFeature.get("calculationType")
          });

          return;
        }
        //

        const coordinate = evt.coordinate;
        const projection = me.map.getView().getProjection();
        const resolution = me.map.getView().getResolution();

        me.queryableLayers = getAllChildLayers(me.map).filter(
          layer =>
            layer.get("queryable") === true && layer.getVisible() === true
        );

        //WMS Requests
        let promiseArray = [];
        me.queryableLayers.forEach(layer => {
          const layerType = getLayerType(layer);
          switch (layerType) {
            case "WFS": {
              let selectedFeatures = me.map.getFeaturesAtPixel(evt.pixel, {
                hitTolerance: 4,
                layerFilter: layerCandidate => {
                  return layerCandidate.get("name") === layer.get("name");
                }
              });
              if (selectedFeatures !== null && selectedFeatures.length > 0) {
                //TODO: If there are more then 2 features selected get the closest one to coordinate rather than the first element
                const clonedFeature = selectedFeatures[0].clone();
                clonedFeature.set("layerName", layer.get("name"));
                me.getInfoResult.push(clonedFeature);
              }
              break;
            }
            case "WMS": {
              let url = layer
                .getSource()
                .getFeatureInfoUrl(coordinate, resolution, projection, {
                  INFO_FORMAT: "application/json"
                });
              promiseArray.push(
                http.get(url, {
                  data: { layerName: layer.get("name") }
                })
              );
              break;
            }
            default:
              break;
          }
        });
        if (promiseArray.length > 0) {
          axios.all(promiseArray).then(function(results) {
            results.forEach(response => {
              const features = response.data.features;
              const layerName = JSON.parse(response.config.data).layerName;
              if (features && features.length === 0) {
                return;
              }
              const olFeatures = geojsonToFeature(response.data, {});

              olFeatures[0].set("layerName", layerName);
              me.getInfoResult.push(olFeatures[0]);
            });

            if (me.getInfoResult.length > 0) {
              me.showPopup();
            }
          });
        } else {
          //Only for WFS layer
          if (me.getInfoResult.length > 0) {
            me.showPopup();
          }
        }
      });
    },
    previousGetInfoLayer() {
      this.popup.currentLayerIndex -= 1;
      this.showPopup();
    },
    nextGetInfoLayer() {
      this.popup.currentLayerIndex += 1;
      this.showPopup();
    },
    getOsmHrefLink() {
      let link = ``;
      if (this.currentInfoFeature && this.currentInfoFeature.get("osm_id")) {
        const feature = this.currentInfoFeature;
        const originGeometry =
          feature.getProperties()["orgin_geometry"] ||
          feature
            .getGeometry()
            .getType()
            .toLowerCase();
        let type;
        switch (originGeometry) {
          case "polygon":
          case "multipolygon":
          case "linestring":
            type = "way";
            break;
          case "point":
            type = "node";
            break;
          default:
            type = null;
            break;
        }
        link =
          `https://www.openstreetmap.org/edit?editor=id&` +
          `${type}` +
          `=${feature.get("osm_id")}`;
      }
      return link;
    },
    getPopupTitle() {
      if (this.getInfoResult[this.popup.currentLayerIndex]) {
        const layer = this.getInfoResult[this.popup.currentLayerIndex];
        const canTranslate = this.$te(
          `map.layerName.${layer.get("layerName")}`
        );
        if (canTranslate) {
          return this.$t(`map.layerName.${layer.get("layerName")}`);
        } else if (
          this.osmMode === true &&
          this.osmMappingLayers[layer.get("layerName")] &&
          this.$te(`map.osmMode.layers.${layer.get("layerName")}.layerName`)
        ) {
          const path = `map.osmMode.layers.${layer.get("layerName")}`;
          return (
            this.$t(`${path}.layerName`) +
            " - " +
            this.$t(`${path}.missingKeyWord`)
          );
        } else {
          return layer.get("layerName");
        }
      }
    },
    ...mapMutations("map", {
      setMap: "SET_MAP",
      setContextMenu: "SET_CONTEXTMENU",
      setLayer: "SET_LAYER"
    }),
    ...mapActions("isochrones", {
      showIsochroneWindow: "showIsochroneWindow"
    })
  },
  computed: {
    ...mapGetters("map", {
      helpTooltip: "helpTooltip",
      currentMessage: "currentMessage",
      osmMode: "osmMode",
      osmMappingLayers: "osmMappingLayers",
      layers: "layers"
    }),
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer"
    }),
    ...mapGetters("user", {
      userId: "userId"
    }),
    ...mapGetters("loader", { isNetworkBusy: "isNetworkBusy" }),
    currentInfo() {
      const feature = this.getInfoResult[this.popup.currentLayerIndex];
      if (!feature) return;
      const props = feature.getProperties();
      let transformed = [];
      const excludedProperties = [
        "id",
        "geometry",
        "geom",
        "orgin_geometry",
        "osm_id",
        "gid",
        "layerName"
      ];
      Object.keys(props).forEach(k => {
        if (!excludedProperties.includes(k) && !typeof k !== "object") {
          transformed.push({
            property: humanize(k),
            value: !props[k] ? "---" : props[k]
          });
        }
      });

      return transformed;
    },
    currentInfoFeature() {
      return this.getInfoResult[this.popup.currentLayerIndex];
    }
  },
  watch: {
    activeInteractions() {
      if (!this.dblClickZoomInteraction) return;
      if (this.activeInteractions.length > 0) {
        this.dblClickZoomInteraction.setActive(false);
      } else {
        this.dblClickZoomInteraction.setActive(true);
      }
    },
    activeColor() {
      this.setOlButtonColor();
    },
    userId(value) {
      setTimeout(() => {
        const layers = Object.keys(this.layers);
        layers.forEach(key => {
          if (
            this.layers[key].get("viewparamsDynamicKeys") &&
            this.layers[key].get("viewparamsDynamicKeys").includes("userId")
          ) {
            if (this.layers[key].getSource().getParams()) {
              let viewparams = this.layers[key].getSource().getParams()
                .viewparams;
              if (!viewparams) {
                viewparams = ``;
              }
              if (!viewparams.includes("userid")) {
                // Insert userId if it doesn't exist.
                viewparams += `userid:${value};`;
                this.layers[key].getSource().updateParams({
                  viewparams
                });
              }
            }
          }
        });
      }, 500);
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
div.ol-attribution {
  bottom: 4px;
  border-radius: 40px;
}

div.ol-control {
  padding: 0px;
  border-radius: 40px;
}

div.ol-control button {
  margin: 0px !important;
}

/* Hover tooltip */
.wg-hover-tooltiptext {
  width: 120px;
  background-color: rgba(211, 211, 211, 0.9);
  color: #222;
  text-align: center;
  padding: 5px;
  border-radius: 6px;

  /* Position the hover tooltip */
  position: absolute;
  z-index: 1;
}

.ol-attribution ul {
  margin: 0;
  padding: 0 0.5em;
  font-size: 0.7rem;
  line-height: 1.375em;
  color: #000;
  text-shadow: 0 0 2px #fff;
}
</style>
