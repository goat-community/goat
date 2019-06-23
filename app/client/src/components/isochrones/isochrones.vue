<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
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
          :class="{ activeIcon: isResultsElVisible, 'mr-2': true }"
          style="margin-right: 2px;"
          small
          >fas fa-bullseye</v-icon
        >
        <h3>{{ $t("isochrones.results.title") }}</h3>
      </v-subheader>

      <div v-show="isResultsElVisible">
        <isochrone-results />
      </div>
    </v-card>
  </v-flex>
</template>

<script>
//Child components
import isochroneOptions from "./isochroneOptions";
import isochroneResults from "./isochroneResults";

//Store & Bus imports
import { EventBus } from "../../EventBus.js";
import { mapActions } from "vuex";

//Ol imports
import { transform } from "ol/proj.js";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import Style from "ol/style/Style";
import Stroke from "ol/style/Stroke";
import Fill from "ol/style/Fill";

export default {
  components: {
    "isochrone-options": isochroneOptions,
    "isochrone-results": isochroneResults
  },
  data: () => ({
    clicked: false,
    isStartPointElVisible: true,
    isOptionsElVisible: true,
    isResultsElVisible: true
  }),
  computed: {},
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
  methods: {
    ...mapActions(["calculateIsochrone"]),
    registerMapClick() {
      const me = this;
      me.map.once("singleclick", me.onMapClick);
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

      this.$store.commit("UPDATE_POSITION", {
        coordinate: coordinateWgs84,
        city: ""
      });
      //Start Isochrone Calculation
      this.calculateIsochrone();
    },

    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneLayer() {
      var me = this;
      let source = new VectorSource();
      var vector = new VectorLayer({
        name: "Isochrone Layer",
        source: source,
        style: new Style({
          fill: new Fill({
            color: "rgba(255, 255, 255, 0.2)"
          }),
          stroke: new Stroke({
            color: "rgba(0, 0, 0, 0.5)",
            width: 2
          })
        })
      });
      me.map.addLayer(vector);
      this.$store.commit("ADD_ISOCHRONE_LAYER", vector);
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
