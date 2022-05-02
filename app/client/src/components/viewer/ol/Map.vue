<template>
  <div id="ol-map-container">
    <!-- Map Controls -->
    <div style="position:absolute;left:20px;top:10px;">
      <search-map
        :viewbox="
          transformExtent(studyArea[0].get('bounds'), 'EPSG:3857', 'EPSG:4326')
        "
        class="mb-2"
        :map="map"
        v-show="!miniViewOlMap"
        :color="appColor.primary"
      />
      <full-screen
        class="mb-2"
        v-show="!miniViewOlMap"
        :color="appColor.primary"
      />
      <measure class="mb-2" v-show="!miniViewOlMap" :color="appColor.primary" />
      <!-- toggle-streetview -->
      <v-tooltip right>
        <template v-slot:activator="{ on }">
          <v-btn
            style="z-index: 1;"
            fab
            dark
            x-small
            v-show="!miniViewOlMap"
            :color="appColor.primary"
            @click="showMiniViewer"
            :loading="isMapillaryBtnDisabled"
            v-on="on"
          >
            <v-icon dark>streetview</v-icon>
          </v-btn>
        </template>
        <span>{{ $t(`map.tooltips.toggleStreetView`) }}</span>
      </v-tooltip>
    </div>

    <progress-status />
    <background-switcher v-show="!miniViewOlMap" />
    <!-- Popup overlay  -->
    <overlay-popup
      :color="appColor.primary"
      :title="getPopupTitle()"
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
        <a
          v-if="currentInfoFeature && currentInfoFeature.get('osm_id')"
          style="text-decoration:none;"
          :href="getOsmHrefLink()"
          target="_blank"
          title=""
        >
          <i class="fa fa-edit"></i> {{ $t("map.popup.editWithOsm") }}</a
        >

        <div
          style="max-height:800px;overflow:hidden;"
          v-if="getInfoResult[popup.currentLayerIndex]"
        >
          <vue-scroll>
            <v-simple-table
              v-if="
                getInfoResult[popup.currentLayerIndex].get('layerName') !==
                  'footpath_visualization'
              "
              dense
              class="pr-2"
            >
              <template v-slot:default>
                <tbody>
                  <tr v-for="item in currentInfo" :key="item.property">
                    <td>{{ item.property }}</td>
                    <td>{{ item.value }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
            <div v-else>
              <indicators-chart
                class="mr-4"
                :feature="getInfoResult[popup.currentLayerIndex]"
              ></indicators-chart>
            </div>
          </vue-scroll>
        </div>
      </template>
    </overlay-popup>
    <!-- Info Snackbar for not visible layers. -->
    <v-snackbar
      :color="appColor.primary"
      top
      :timeout="visibilityLayerSnackbar.timeout"
      v-model="visibilityLayerSnackbar.state"
    >
      <v-icon color="white" class="mr-3">
        info
      </v-icon>
      <span v-html="visibilityLayerSnackbar.message"></span>
      <v-btn text @click="visibilityLayerSnackbar.state = false">
        <v-icon>close</v-icon>
      </v-btn>
    </v-snackbar>

    <!-- Info snackbar when editing a layer -->
    <v-snackbar
      :color="selectedEditLayer ? scenarioLayerEditModeColor : appColor.primary"
      v-if="activeScenario"
      :timeout="0"
      style="font-size:16px;"
      :value="activeScenario ? true : false"
    >
      <v-select
        :style="
          selectedEditLayer
            ? `border-right: 1px solid grey;width: 200px;`
            : 'width: 150px;'
        "
        dark
        hide-details
        :class="{
          'mx-3 mt-0 pt-0': true,
          'pr-4': !!selectedEditLayer
        }"
        :items="calculationMode.values"
        v-model="calculationMode.active"
      >
        <template slot="selection" slot-scope="{ item }">
          {{
            $te(`isochrones.options.${item}`)
              ? $t(`isochrones.options.${item}`).toUpperCase()
              : item.toUpperCase()
          }}
        </template>
        <template slot="item" slot-scope="{ item }">
          {{
            $te(`isochrones.options.${item}`)
              ? $t(`isochrones.options.${item}`).toUpperCase()
              : item.toUpperCase()
          }}
        </template>
      </v-select>
      <span v-if="selectedEditLayer" class="h2"
        >{{
          $te(`map.snackbarMessages.scenarioEditMode`)
            ? $t(`map.snackbarMessages.scenarioEditMode`).toUpperCase()
            : "EDIT MODE"
        }}
      </span>
      <v-btn
        v-if="selectedEditLayer"
        color="error"
        text
        @click="selectedEditLayer = null"
      >
        {{ $te(`buttonLabels.exit`) ? $t(`buttonLabels.exit`) : "Exit" }}
      </v-btn>
    </v-snackbar>
    <v-snackbar
      :color="appColor.primary"
      v-if="isRecomputingHeatmap"
      :timeout="0"
      top
      center
      style="font-size:14px;"
      :value="isRecomputingHeatmap"
    >
      <span
        >{{
          $te(`heatmap.recomputingHeatmaps`)
            ? $t(`heatmap.recomputingHeatmaps`)
            : "Recomputing Heatmaps... "
        }}
      </span>
      <v-progress-circular indeterminate color="white"></v-progress-circular>
    </v-snackbar>
  </div>
</template>

<script>
import Vue from "vue";
import Map from "ol/Map";
import View from "ol/View";

// ol imports
import Overlay from "ol/Overlay";
import Feature from "ol/Feature";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import VectorImageLayer from "ol/layer/VectorImage";
import LineString from "ol/geom/LineString";
import { transformExtent } from "ol/proj";

// style imports
import {
  getInfoStyle,
  studyAreaStyle,
  poisAoisStyle
} from "../../../style/OlStyleDefs";
// import the app-wide EventBus
import { EventBus } from "../../../EventBus";

// utils imports
import { LayerFactory } from "../../../factory/layer.js";
import { humanize, isCssColor } from "../../../utils/Helpers";
import { getAllChildLayers } from "../../../utils/Layer";
import { geojsonToFeature } from "../../../utils/MapUtils";
import axios from "axios";

//Store imports
import { mapMutations, mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";

//Map Controls
import OverlayPopup from "./controls/Overlay";
import MapLoadingProgressStatus from "./controls/MapLoadingProgressStatus";
import BackgroundSwitcher from "./controls/BackgroundSwitcher";
import FullScreen from "./controls/Fullscreen";
import Measure from "./controls/Measure";
import Search from "./controls/Search.vue";
import DoubleClickZoom from "ol/interaction/DoubleClickZoom";

import { defaults as defaultControls, Attribution } from "ol/control";
import { defaults as defaultInteractions } from "ol/interaction";

import { debounce } from "../../../utils/Helpers";
// Context menu
import ContextMenu from "ol-contextmenu/dist/ol-contextmenu";
import "ol-contextmenu/dist/ol-contextmenu.min.css";

// Indicators Chart
import IndicatorsChart from "../../other/IndicatorsChart";
import { GET_POIS_AOIS } from "../../../store/actions.type";

export default {
  components: {
    "overlay-popup": OverlayPopup,
    "progress-status": MapLoadingProgressStatus,
    "background-switcher": BackgroundSwitcher,
    "full-screen": FullScreen,
    "indicators-chart": IndicatorsChart,
    "search-map": Search,
    measure: Measure
  },
  name: "app-ol-map",
  props: {
    miniViewOlMap: { type: Boolean, required: true, default: false }
  },
  data() {
    return {
      queryableLayers: [],
      activeInteractions: [],
      popup: {
        rawHtml: null,
        title: "info",
        isVisible: false,
        currentLayerIndex: 0
      },
      getInfoResult: [],
      limitedVisibilityLayers: [],
      visibilityLayerSnackbar: {
        state: false,
        message: "",
        timeout: 8000
      }
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
      EventBus.$on("toggleLayerVisiblity", this.showNonVisibleLayersInfo);
    }, 200);
  },
  created() {
    var me = this;
    // Make map rotateable according to property
    const attribution = new Attribution({
      collapsible: true,
      collapsed: false
    });

    //Need to reference as we should deactive double click zoom when there
    //are active interaction like draw/modify
    this.dblClickZoomInteraction = new DoubleClickZoom();
    me.map = new Map({
      layers: [],
      interactions: defaultInteractions({
        doubleClickZoom: false,
        mouseWheelZoom: true
      }).extend([this.dblClickZoomInteraction]),
      controls: defaultControls({
        attribution: false,
        zoom: false
      }).extend([attribution]),
      view: new View({
        extent: me.studyArea[0].get("bounds"),
        center: me.appConfig.map.center || [0, 0],
        zoom: me.appConfig.map.zoom,
        minZoom: me.appConfig.map.minZoom,
        maxZoom: me.appConfig.map.maxZoom || 19
      })
    });
    // Get study area
    me.createStudyAreaLayer();
    // Create poisaoisLayer
    me.createPoisAoisLayer();
    // Create layers from config and add them to map
    const layers = me.createLayers();
    me.map.getLayers().extend(layers);
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
  },

  methods: {
    /**
     * Creates the OL layers due to the map "layers" array in app config.
     * @return {ol.layer.Base[]} Array of OL layer instances
     */
    createLayers() {
      let layers = [];
      this.appConfig.layer_groups.forEach(group => {
        const groupName = Object.keys(group)[0];
        group[groupName].children.forEach(lConf => {
          const layerName = Object.keys(lConf)[0];
          lConf = lConf[layerName];
          lConf.name = layerName;
          if (lConf.type) {
            try {
              const olLayer = LayerFactory.getInstance({
                group: groupName,
                ...lConf
              });
              if (olLayer.get("name") === "sub_study_area") {
                this.subStudyAreaLayer = olLayer;
              }
              if (olLayer) {
                if (
                  ![Infinity, undefined, null].includes(
                    olLayer.getMaxResolution()
                  )
                ) {
                  this.limitedVisibilityLayers.push(olLayer);
                }
                layers.push(olLayer);
              }
            } catch (error) {
              console.log(error);
            }
          }
        });
      });
      return layers;
    },
    /**
     * Creates the study area layer.
     */
    createStudyAreaLayer() {
      const source = new VectorSource({
        wrapX: false
      });
      const vector = new VectorImageLayer({
        name: "study_area",
        displayInLayerList: true,
        type: "VECTOR",
        group: "buildings_landuse",
        zIndex: 100,
        source: source,
        style: studyAreaStyle
      });
      this.getInfoLayerSource = source;
      source.addFeature(this.studyArea[0]);
      this.map.addLayer(vector);
      this.map.getView().fit(source.getExtent());
    },
    /**
     * Creates pois aois layer
     */
    createPoisAoisLayer() {
      const vector = new VectorLayer({
        name: "pois_aois_layer",
        type: "VECTOR",
        displayInLayerList: false,
        queryable: true,
        zIndex: 99,
        source: new VectorSource(),
        style: poisAoisStyle
      });
      this.map.addLayer(vector);
      this.poisAoisLayer = vector;
      this.$store.dispatch(`poisaois/${GET_POIS_AOIS}`);
    },

    /**
     * Creates a layer to visualize selected GetInfo features.
     */
    createGetInfoLayer() {
      const source = new VectorSource({
        wrapX: false
      });
      const vector = new VectorLayer({
        name: "get_info",
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
      // Show snackbar info when layers aren't visible in the current resolution
      map.getView().on("change:resolution", this.showNonVisibleLayersInfo);
    },

    /**
     * Sets the background color of the OL buttons to the color property.
     */
    setOlButtonColor() {
      var me = this;

      if (isCssColor(me.appColor.primary)) {
        // directly apply the given CSS color
        const rotateEl = document.querySelector(".ol-rotate");
        if (rotateEl) {
          rotateEl.className += " elevation-5";
          rotateEl.borderRadius = "40px";
          const rotateElStyle = document.querySelector(
            ".ol-rotate .ol-rotate-reset"
          ).style;
          rotateElStyle.backgroundColor = me.appColor.primary;
          rotateElStyle.borderRadius = "40px";
        }
        const attrEl = document.querySelector(".ol-attribution");
        if (attrEl) {
          attrEl.className += " elevation-5";
          const elStyle = document.querySelector(
            ".ol-attribution button[type='button']"
          ).style;
          elStyle.backgroundColor = me.appColor.primary;
          elStyle.borderRadius = "40px";
        }
      } else {
        // apply vuetify color by transforming the color to the corresponding
        // CSS class (see https://vuetifyjs.com/en/framework/colors)
        const [colorName, colorModifier] = me.appColor.primary
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
        positioning: "bottom-left",
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
    showPopup(coordinate) {
      // Clear highligh feature
      this.getInfoLayerSource.clear();
      const infoFeature = this.getInfoResult[this.popup.currentLayerIndex];
      let position = infoFeature.getGeometry()
        ? infoFeature.getGeometry().getCoordinates()
        : coordinate;
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
            if (
              ["isochrone_layer", "pois_aois_layer"].includes(
                candidate.get("name")
              )
            ) {
              return true;
            }
            return false;
          }
        });
        const style = this.map.getTarget().style;
        if (!style) return false;
        if (features.length > 0) {
          style.cursor = "pointer";
        } else {
          style.cursor = "";
        }
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
        const isochroneFeatures = me.map.getFeaturesAtPixel(evt.pixel, {
          layerFilter: candidate => {
            if (candidate.get("name") === "isochrone_layer") {
              return true;
            }
            return false;
          }
        });
        const otherFeatures = me.map.getFeaturesAtPixel(evt.pixel, {
          layerFilter: candidate => {
            if (candidate.get("name") !== "isochrone_layer") {
              return true;
            }
            return false;
          }
        });
        if (isochroneFeatures.length > 0 && otherFeatures.length === 0) {
          // Toggle thematic data for isochrone window
          const isochroneFeature = isochroneFeatures[0];
          EventBus.$emit(
            "show-isochrone-window",
            isochroneFeature.get("calculationNumber")
          );
          return;
        }

        me.queryableLayers = getAllChildLayers(me.map).filter(
          layer =>
            layer.get("queryable") === true && layer.getVisible() === true
        );

        //WMS Requests
        let promiseArray = [];
        me.queryableLayers.forEach(layer => {
          const layerType = layer.get("type");
          switch (layerType) {
            case "WFS":
            case "VECTOR":
            case "MVT":
            case "GEOBUF":
            case "VECTORTILE": {
              let selectedFeatures = me.map.getFeaturesAtPixel(evt.pixel, {
                hitTolerance: 4,
                layerFilter: layerCandidate => {
                  return layerCandidate.get("name") === layer.get("name");
                }
              });
              if (selectedFeatures !== null && selectedFeatures.length > 0) {
                //TODO: If there are more then 2 features selected get the closest one to coordinate rather than the first element
                let clonedFeature;

                if (!selectedFeatures[0].clone) {
                  // !!! Workaround for vector tile features.
                  const vtProps = {
                    layerName: layer.get("name"),
                    osm_type: selectedFeatures[0].getType()
                  };

                  Object.assign(vtProps, selectedFeatures[0].getProperties());
                  const flatCoordinates = selectedFeatures[0].getFlatCoordinates();
                  if (flatCoordinates && flatCoordinates.length > 0) {
                    const _coordinates = [];
                    const _values = Object.values(flatCoordinates);
                    for (let i = 0; i < _values.length; i += 2) {
                      _coordinates.push(_values.slice(i, i + 2));
                    }

                    const geometry = new LineString(_coordinates, "XY");
                    vtProps.geometry = geometry;
                  }
                  clonedFeature = new Feature(vtProps);
                } else {
                  clonedFeature = selectedFeatures[0].clone();
                  clonedFeature.set("layerName", layer.get("name"));
                }
                me.getInfoResult.push(clonedFeature);
              }
              break;
            }
            default:
              break;
          }
        });
        if (promiseArray.length > 0) {
          console.log(promiseArray);
          axios.all(promiseArray).then(function(results) {
            console.log(results);
            results.forEach(response => {
              if (response && response.data && response.data.features) {
                const features = response.data.features;
                const layerName = JSON.parse(response.config.data).layerName;
                if (features && features.length === 0) {
                  return;
                }
                const olFeatures = geojsonToFeature(response.data, {});

                olFeatures[0].set("layerName", layerName);
                me.getInfoResult.push(olFeatures[0]);
              }
            });
            if (me.getInfoResult.length > 0) {
              me.showPopup(evt.coordinate);
            }
          });
        } else {
          //Only for WFS layer
          if (me.getInfoResult.length > 0) {
            me.showPopup(evt.coordinate);
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

    showNonVisibleLayersInfo: debounce(function() {
      const currentResolution = this.map.getView().getResolution();
      const notVisibleLayers = [];
      this.limitedVisibilityLayers.forEach(layer => {
        if (
          layer.getMaxResolution() &&
          layer.getMaxResolution() < currentResolution &&
          layer.getVisible()
        ) {
          const layerName = this.$te(`map.layerName.${layer.get("name")}`)
            ? this.$t(`map.layerName.${layer.get("name")}`)
            : layerName;
          notVisibleLayers.push(layerName);
        }
      });

      if (notVisibleLayers.length > 0) {
        this.visibilityLayerSnackbar = {
          state: true,
          message: `${this.$t(
            `map.snackbarMessages.zoomInToShowFeatures`
          )}: <b>${notVisibleLayers.toString()}</b>`,
          timeout: 80000
        };
      } else {
        this.visibilityLayerSnackbar = {
          state: false,
          message: ``,
          timeout: 0
        };
      }
    }, 200),
    getOsmHrefLink() {
      let link = ``;
      if (this.currentInfoFeature && this.currentInfoFeature.get("osm_id")) {
        const feature = this.currentInfoFeature;

        let type = feature.get("osm_type");
        if (!type && feature.get("orgin_geometry")) {
          const originGeometry =
            feature.getProperties()["orgin_geometry"] ||
            feature
              .getGeometry()
              .getType()
              .toLowerCase();
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
        } else {
          return layer.get("layerName");
        }
      } else {
        return "";
      }
    },
    transformExtent,
    showMiniViewer() {
      this.miniViewerVisible = true;
      this.isMapillaryBtnDisabled = true;
    },
    ...mapMutations("map", {
      setContextMenu: "SET_CONTEXTMENU",
      setLayer: "SET_LAYER",
      toggleSnackbar: "TOGGLE_SNACKBAR"
    }),
    ...mapMutations("pois", {
      init: "INIT"
    })
  },
  computed: {
    ...mapFields("map", {
      subStudyAreaLayer: "subStudyAreaLayer",
      selectedEditLayer: "selectedEditLayer",
      isMapillaryBtnDisabled: "isMapillaryBtnDisabled",
      miniViewerVisible: "miniViewerVisible"
    }),
    ...mapFields("poisaois", {
      poisAoisLayer: "poisAoisLayer",
      selectedPoisAois: "selectedPoisAois",
      poisAois: "poisAois"
    }),

    ...mapGetters("map", {
      studyArea: "studyArea",
      helpTooltip: "helpTooltip",
      currentMessage: "currentMessage",
      layers: "layers"
    }),
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig",
      scenarioLayerEditModeColor: "scenarioLayerEditModeColor",
      isRecomputingHeatmap: "isRecomputingHeatmap",
      calculationMode: "calculationMode"
    }),
    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer",
      options: "options"
    }),
    ...mapGetters("scenarios", {
      activeScenario: "activeScenario"
    }),
    ...mapGetters("loader", { isNetworkBusy: "isNetworkBusy" }),
    currentInfo() {
      const feature = this.getInfoResult[this.popup.currentLayerIndex];
      if (!feature) return;
      const props = feature.getProperties();
      let transformed = [];
      const excludedProperties = [
        "uid",
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
    appColor() {
      this.setOlButtonColor();
    },
    // Edge case for pois layer style. We have to restructure the state of selected pois as a key value pair (category: state)
    // in order to use it in the style (getters can't be accessed outside vue component).
    // As the selectedPoisState is also changed from editing component
    // this should be watched here as it might be that poisAoisTree component is not rendered yet.
    selectedPoisAois(selected) {
      const poisAois = {};
      selected.forEach(item => {
        poisAois[item.value] = true;
      });
      this.poisAois = poisAois;
      this.poisAoisLayer.changed();
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
