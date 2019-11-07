<template>
  <!-- Popup overlay  -->
  <overlay-popup :title="popup.title" v-show="popup.isVisible" ref="popup">
    <v-btn icon>
      <v-icon>close</v-icon>
    </v-btn>
    <template v-slot:close>
      <v-btn @click="closePopup()" icon>
        <v-icon>close</v-icon>
      </v-btn>
    </template>
    <template v-slot:body>
      <span v-html="popup.rawHtml"></span>
      <v-divider></v-divider>
      <v-data-table
        :headers="getInfoHeader"
        :items="getInfoResult"
        hide-default-header
        hide-default-footer
        dense
        flat
      ></v-data-table>
      <v-divider></v-divider>
    </template>
  </overlay-popup>
</template>

<script>
// helper function to detect a CSS color
// Taken from Vuetify sources
// https://github.com/vuetifyjs/vuetify/blob/master/packages/vuetify/src/mixins/colorable.ts
function isCssColor(color) {
  return !!color && !!color.match(/^(#|(rgb|hsl)a?\()/);
}

import Vue from "vue";
import Map from "ol/Map";
import View from "ol/View";
import { defaults as defaultInteractions } from "ol/interaction";
import Overlay from "ol/Overlay";
import Mask from "ol-ext/filter/Mask";
import OlFill from "ol/style/Fill";
// import the app-wide EventBus
import { EventBus } from "../../EventBus";
import { LayerFactory } from "../../factory/layer.js";

import { mapGetters } from "vuex";
import { groupBy, humanize } from "../../utils/Helpers";
import { getAllChildLayers } from "../../utils/Layer";
import { geojsonToFeature } from "../../utils/MapUtils";
import { Group as LayerGroup } from "ol/layer.js";

import http from "../../services/http";

import OverlayPopup from "./Overlay";

//Store imports
import { mapMutations } from "vuex";

export default {
  components: {
    "overlay-popup": OverlayPopup
  },
  name: "app-map",
  props: {
    color: { type: String, required: false, default: "green darken-3" }
  },
  data() {
    return {
      zoom: this.$appConfig.map.zoom,
      center: this.$appConfig.map.center,
      minZoom: this.$appConfig.map.minZoom,
      maxZoom: this.$appConfig.map.maxZoom,
      allLayers: [],
      activeInteractions: [],
      popup: {
        rawHtml: null,
        title: "info",
        isVisible: false
      },
      getInfoHeader: [
        { text: "Property", value: "property" },
        { text: "Value", value: "value" }
      ],
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
      me.createPopupOverlay();
    }, 200);
  },
  created() {
    var me = this;

    // make map rotateable according to property
    const interactions = defaultInteractions({
      altShiftDragRotate: me.rotateableMap
    });

    me.map = new Map({
      layers: [],
      interactions: interactions,
      view: new View({
        center: me.center || [0, 0],
        zoom: me.zoom,
        minZoom: me.minZoom,
        maxZoom: me.maxZoom
      })
    });

    // create layers from config and add them to map
    const layers = me.createLayers();
    me.map.getLayers().extend(layers);
    //Create mask filters
    me.createMaskFilters(layers);

    EventBus.$on("ol-interaction-activated", startedInteraction => {
      me.activeInteractions.push(startedInteraction);
    });
    EventBus.$on("ol-interaction-stoped", stopedInteraction => {
      me.activeInteractions = Array.from(new Set(me.activeInteractions));
      me.activeInteractions = me.activeInteractions.filter(interaction => {
        return interaction !== stopedInteraction;
      });
    });
  },

  methods: {
    /**
     * Creates the OL layers due to the map "layers" array in app config.
     * @return {ol.layer.Base[]} Array of OL layer instances
     */
    createLayers() {
      let layers = [];
      const layersConfigGrouped = groupBy(this.$appConfig.map.layers, "group");
      for (var group in layersConfigGrouped) {
        if (!layersConfigGrouped.hasOwnProperty(group)) {
          continue;
        }
        const mapLayers = [];
        layersConfigGrouped[group].reverse().forEach(function(lConf) {
          const layer = LayerFactory.getInstance(lConf);
          mapLayers.push(layer);
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
     * Creates a filter mask of the city using ol mask extension.
     * Hides other municipalities and states.
     */
    createMaskFilters(mapLayers) {
      const me = this;

      //Filter background layers
      const backgroundLayers = [];
      mapLayers.forEach(layer => {
        if (layer.get("name") === "backgroundLayers") {
          backgroundLayers.push(...layer.getLayers().getArray());
        }
      });

      //Reference study area layer
      let studyAreaLayer;
      getAllChildLayers(me.map).forEach(layer => {
        if (layer.get("name") === "studyArea") {
          studyAreaLayer = layer;
        }
      });

      //Create masks
      if (studyAreaLayer) {
        studyAreaLayer.getSource().on("change", function() {
          const feature = studyAreaLayer.getSource().getFeatures()[0];
          const bbox = feature
            .clone()
            .getGeometry()
            .transform("EPSG:3857", "EPSG:4326")
            .getExtent()
            .toString();
          me.setStudyAreaBbox(bbox);
          const mask = new Mask({
            feature: feature,
            inner: false,
            fill: new OlFill({ color: [169, 169, 169, 0.8] })
          });
          for (const i of backgroundLayers) {
            i.addFilter(mask);
          }
        });
      }
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
     * Sets the background color of the OL buttons to the color property.
     */
    setOlButtonColor() {
      var me = this;

      if (isCssColor(me.color)) {
        // directly apply the given CSS color
        if (document.querySelector(".ol-zoom")) {
          document.querySelector(".ol-zoom .ol-zoom-in").style.backgroundColor =
            me.color;
          document.querySelector(
            ".ol-zoom .ol-zoom-out"
          ).style.backgroundColor = me.color;
        }
        if (document.querySelector(".ol-rotate")) {
          document.querySelector(
            ".ol-rotate .ol-rotate-reset"
          ).style.backgroundColor = me.color;
        }

        if (document.querySelector(".ol-attribution")) {
          document.querySelector(
            ".ol-attribution button[type='button']"
          ).style.backgroundColor = me.color;
        }
      } else {
        // apply vuetify color by transforming the color to the corresponding
        // CSS class (see https://vuetifyjs.com/en/framework/colors)
        const [colorName, colorModifier] = me.color
          .toString()
          .trim()
          .split(" ", 2);
        if (document.querySelector(".ol-zoom")) {
          document
            .querySelector(".ol-zoom .ol-zoom-in")
            .classList.add(colorName);
          document
            .querySelector(".ol-zoom .ol-zoom-in")
            .classList.add(colorModifier);
          document
            .querySelector(".ol-zoom .ol-zoom-out")
            .classList.add(colorName);
          document
            .querySelector(".ol-zoom .ol-zoom-out")
            .classList.add(colorModifier);
        }
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
    },

    /**
     * Map click event for "Get Info" Module.
     */
    setupMapClick() {
      const me = this;
      const map = me.map;
      me.mapClickListenerKey = map.on("click", evt => {
        if (me.activeInteractions.length > 0) {
          me.popupOverlay.setPosition(undefined);
          return;
        }
        const coordinate = evt.coordinate;
        const projection = me.map.getView().getProjection();
        const resolution = me.map.getView().getResolution();
        let layerToQuery;
        getAllChildLayers(me.map).forEach(layer => {
          if (layer.get("queryable") === true) {
            layerToQuery = layer;
          }
        });
        if (!layerToQuery || layerToQuery.getVisible() == false) {
          return;
        }
        const url = layerToQuery
          .getSource()
          .getGetFeatureInfoUrl(coordinate, resolution, projection, {
            INFO_FORMAT: "application/json"
          });
        http.get(url).then(function(response) {
          const features = response.data.features;
          if (features.length === 0) {
            me.popupOverlay.setPosition(undefined);
            return;
          }

          const olFeatures = geojsonToFeature(response.data, {});
          const featureCoordinates = olFeatures[0]
            .getGeometry()
            .getCoordinates();
          const props = olFeatures[0].getProperties();

          let overlayCoordinates;
          if (olFeatures[0].getGeometry().getType() === "Point") {
            overlayCoordinates = featureCoordinates;
          } else {
            overlayCoordinates = featureCoordinates[0];
          }

          me.popupOverlay.setPosition(overlayCoordinates);
          me.popup.isVisible = true;
          me.popup.title = `info`;

          if (layerToQuery.get("name") === "pois") {
            const osmId = props["osm_id"];
            const originGeometry = props["orgin_geometry"];
            if (osmId !== null) {
              let type;
              switch (originGeometry) {
                case "polygon":
                  type = "way";
                  break;
                case "point":
                  type = "node";
                  break;
                default:
                  type = null;
                  break;
              }

              me.popup.rawHtml = `<a style="text-decoration:none;" 
                                        href="https://www.openstreetmap.org/edit?editor=id&${type}=${osmId}" target="_blank" title="">
                              <i class="fa fa-edit"></i> ${me.$t(
                                "map.popup.editWithOsm"
                              )}</a>`;
            }
          }

          const excludedProperties = ["geometry", "orgin_geometry", "osm_id"];
          let transformed = [];
          Object.keys(props).forEach(k => {
            if (!excludedProperties.includes(k)) {
              transformed.push({
                property: humanize(k),
                value: props[k] === null ? "---" : props[k]
              });
            }
          });

          me.getInfoResult = transformed;
        });
      });
    },
    ...mapMutations("map", {
      setStudyAreaBbox: "SET_STUDYAREA_BBOX",
      setMap: "SET_MAP"
    })
  },
  computed: {
    ...mapGetters("map", {
      helpTooltip: "helpTooltip",
      currentMessage: "currentMessage"
    })
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
div.ol-zoom {
  top: auto;
  left: auto;
  top: 1em;
  left: 1em;
}

div.ol-attribution {
  bottom: 0px;
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
</style>
