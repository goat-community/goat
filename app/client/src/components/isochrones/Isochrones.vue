<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <!-- THEMATIC DATA -->
      <template v-if="isThematicDataVisible === true">
        <v-card-title primary-title class="py-2">
          <v-btn
            flat
            class="my-0 py-0"
            icon
            light
            @click="toggleThematicDataVisibility(false)"
          >
            <v-icon color="rgba(0,0,0,0.54)">fas fa-arrow-left</v-icon>
          </v-btn>
          <span class="title font-weight-regular">Thematic Data</span>
        </v-card-title>
        <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
          <v-divider></v-divider>
        </v-card-text>

        <isochrone-thematic-data />
      </template>

      <!-- ISOCHRONE OPTIONS AND RESULTS  -->
      <template v-else>
        <v-card-title primary-title>
          <span class="title font-weight-regular">{{
            $t("isochrones.title")
          }}</span>
        </v-card-title>
        <v-card-text class="pr-16 pl-16 pt-0 pb-0">
          <v-divider></v-divider>
        </v-card-text>
        <v-card-text>
          <v-layout row>
            <v-flex xs12>
              <v-text-field
                solo
                label="Starting Point"
                hide-details
                prepend-inner-icon="search"
              ></v-text-field>
            </v-flex>
            <v-flex xs2>
              <v-btn fab small flat @click="registerMapClick">
                <v-icon color="#30C2FF">fas fa-map-marker-alt</v-icon>
              </v-btn>
            </v-flex>
          </v-layout>
        </v-card-text>
        <v-card-text class="pr-16 pl-16 pt-0 pb-0">
          <v-divider></v-divider>
        </v-card-text>

        <!-- Isochrone Options -->
        <v-subheader
          class="clickable"
          @click="isOptionsElVisible = !isOptionsElVisible"
        >
          <v-icon
            :class="{ activeIcon: isOptionsElVisible, 'mr-2': true }"
            small
            class="mr-2"
            >fas fa-sliders-h</v-icon
          >
          <h3>{{ $t("isochrones.options.title") }}</h3>
        </v-subheader>
        <div v-show="isOptionsElVisible">
          <isochrone-options />
        </div>

        <!-- Isochrone Results  -->
        <v-card-text class="pr-16 pl-16 pt-0 pb-0">
          <v-divider></v-divider>
        </v-card-text>
        <v-subheader
          class="clickable"
          @click="isResultsElVisible = !isResultsElVisible"
        >
          <v-icon
            :class="{
              activeIcon: isResultsElVisible,
              'mr-2': true
            }"
            style="margin-right: 2px;"
            small
            >fas fa-bullseye</v-icon
          >
          <h3>{{ $t("isochrones.results.title") }}</h3>
        </v-subheader>

        <div v-show="isResultsElVisible">
          <isochrone-results />
        </div>
      </template>
      <!-- -- -->
    </v-card>
  </v-flex>
</template>

<script>
//Child components
import IsochroneOptions from "./IsochroneOptions";
import IsochroneResults from "./IsochroneResults";
import IsochronThematicData from "./IsochronesThematicData";

//Store & Bus imports
import { EventBus } from "../../EventBus.js";
import { mapGetters, mapActions, mapMutations } from "vuex";

//Ol imports
import { transform } from "ol/proj.js";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import { Style, Stroke, Fill, Icon } from "ol/style";

export default {
  components: {
    "isochrone-options": IsochroneOptions,
    "isochrone-results": IsochroneResults,
    "isochrone-thematic-data": IsochronThematicData
  },
  data: () => ({
    clicked: false,
    isStartPointElVisible: true,
    isOptionsElVisible: true,
    isResultsElVisible: true
  }),
  created() {
    var me = this;
    // Listen to the ol-map-mounted event and receive the OL map instance
    EventBus.$on("ol-map-mounted", olMap => {
      // make the OL map accesible in this component
      me.map = olMap;

      //Create isochrone layer
      me.createIsochroneLayer();
    });
  },
  computed: {
    ...mapGetters("isochrones", {
      styleData: "styleData",
      isThematicDataVisible: "isThematicDataVisible"
    }),
    ...mapGetters("map", { messages: "messages" })
  },
  methods: {
    ...mapActions("isochrones", { calculateIsochrone: "calculateIsochrone" }),
    ...mapMutations("isochrones", {
      addStyleInCache: "ADD_STYLE_IN_CACHE",
      updatePosition: "UPDATE_POSITION",
      addIsochroneLayer: "ADD_ISOCHRONE_LAYER",
      toggleThematicDataVisibility: "TOGGLE_THEMATIC_DATA_VISIBILITY"
    }),

    ...mapMutations("map", {
      startHelpTooltip: "START_HELP_TOOLTIP",
      stopHelpTooltip: "STOP_HELP_TOOLTIP"
    }),
    registerMapClick() {
      const me = this;
      me.map.once("singleclick", me.onMapClick);
      me.startHelpTooltip(me.messages.interaction.calculateIsochrone);
      me.map.getTarget().style.cursor = "pointer";
    },
    /**
     * Handler for 'singleclick' on the map.
     * Collects data and passes it to corresponding objects.
     * @param  {ol/MapBrowserEvent} evt The OL event of 'singleclick' on the map
     */
    onMapClick(evt) {
      const me = this;
      //Update Isochrone Position (City or Coordinate)
      const projection = me.map
        .getView()
        .getProjection()
        .getCode();

      const coordinateWgs84 = transform(
        evt.coordinate,
        projection,
        "EPSG:4326"
      );

      me.updatePosition({
        coordinate: coordinateWgs84,
        city: ""
      });
      //Start Isochrone Calculation
      me.calculateIsochrone();
      me.stopHelpTooltip();
      me.map.getTarget().style.cursor = "";
    },

    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneLayer() {
      let me = this;
      let vector = new VectorLayer({
        name: "Isochrone Layer",
        source: new VectorSource(),
        style: feature => {
          // Style array
          let styles = [];
          let styleData = me.styleData;
          // Get the incomeLevel and modus from the feature properties
          let level = feature.get("step");
          let modus = feature.get("modus");
          let isVisible = feature.get("isVisible");

          let geomType = feature.getGeometry().getType();

          /**
           * Creates styles for isochrone polygon geometry type and isochrone
           * center marker.
           */
          if (
            geomType === "Polygon" ||
            geomType === "MultiPolygon" ||
            geomType === "LineString"
          ) {
            //Check feature isVisible Property
            if (isVisible === false) {
              return;
            }

            //Fallback isochrone style
            if (!modus) {
              if (!styleData.styleCache.default["GenericIsochroneStyle"]) {
                let genericIsochroneStyle = new Style({
                  fill: new Fill({
                    color: [0, 0, 0, 0]
                  }),
                  stroke: new Stroke({
                    color: "#0d0d0d",
                    width: 7
                  })
                });
                let payload = {
                  style: genericIsochroneStyle,
                  isochroneType: "default",
                  styleName: "GenericIsochroneStyle"
                };
                this.addStyleInCache(payload);
              }
              styles.push(
                styleData.styleCache.default["GenericIsochroneStyle"]
              );
            }
            // If the modus is 1 it is a default isochrone
            if (modus === 1 || modus === 3) {
              if (!styleData.styleCache.default[level]) {
                let style = new Style({
                  stroke: new Stroke({
                    color: feature.get("color"),
                    width: 5
                  })
                });
                let payload = {
                  style: style,
                  isochroneType: "default",
                  styleName: level
                };
                this.addStyleInCache(payload);
              }
              styles.push(styleData.styleCache.default[level]);
            } else {
              if (!styleData.styleCache.input[level]) {
                let style = new Style({
                  stroke: new Stroke({
                    color: feature.get("color"),
                    width: 5
                  })
                });
                let payload = {
                  style: style,
                  isochroneType: "input",
                  styleName: level
                };
                this.addStyleInCache(payload);
              }
              styles.push(styleData.styleCache.input[level]);
            }
          } else {
            let path = `img/markers/marker-${feature.get(
              "calculationNumber"
            )}.png`;
            let markerStyle = new Style({
              image: new Icon({
                anchor: [0.5, 0.96],
                src: path,
                scale: 0.5
              })
            });
            styles.push(markerStyle);
          }
          return styles;
        }
      });
      me.map.addLayer(vector);
      this.addIsochroneLayer(vector);
    }
  },
  mounted() {}
};
</script>
<style lang="css" scoped>
.activeIcon {
  color: #30c2ff;
}
</style>
