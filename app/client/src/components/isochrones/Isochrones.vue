<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <!-- ISOCHRONES  -->
      <template>
        <isochrone-type />

        <isochrone-start-single v-if="options.calculationType === 'single'" />
        <isochrone-start-multiple
          v-if="options.calculationType === 'multiple'"
        />
        <isochrone-options />
        <isochrone-results id="isochroneResultsEl" />
      </template>
      <!-- -- -->
    </v-card>
    <confirm ref="confirm"></confirm>
  </v-flex>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import { Isochrones } from "../../mixins/Isochrones";

//Child components
import IsochroneOptions from "./IsochroneOptions";
import IsochroneResults from "./IsochroneResults";
import IsochroneType from "./IsochroneType";
import IsochroneStartSingle from "./IsochroneStartSingle";
import IsochroneStartMultiple from "./IsochroneStartMultiple";

import {
  getIsochroneStyle,
  getIsochroneNetworkStyle
} from "../../style/OlStyleDefs";

//Store imports
import { mapGetters, mapMutations, mapActions } from "vuex";

//Ol imports
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import VectorImageLayer from "ol/layer/VectorImage";

export default {
  mixins: [Mapable, Isochrones],
  components: {
    "isochrone-options": IsochroneOptions,
    "isochrone-results": IsochroneResults,
    "isochrone-type": IsochroneType,
    "isochrone-start-single": IsochroneStartSingle,
    "isochrone-start-multiple": IsochroneStartMultiple
  },
  computed: {
    ...mapGetters("isochrones", {
      styleData: "styleData",
      options: "options",
      calculations: "calculations"
    }),
    ...mapGetters("map", {
      contextmenu: "contextmenu"
    })
  },
  methods: {
    ...mapMutations("isochrones", {
      init: "INIT",
      addStyleInCache: "ADD_STYLE_IN_CACHE",
      addIsochroneLayer: "ADD_ISOCHRONE_LAYER",
      addIsochroneNetworkLayer: "ADD_ISOCHRONE_ROAD_NETWORK_LAYER"
    }),
    ...mapActions("isochrones", {
      removeCalculation: "removeCalculation"
    }),

    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.createIsochroneLayer();
      this.createIsochroneRoadNetworkLayer();
      this.setUpCtxMenu();
    },

    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneLayer() {
      const me = this;
      const style = getIsochroneStyle(me.styleData, me.addStyleInCache);
      const vector = new VectorLayer({
        name: "Isochrone Layer",
        zIndex: 7,
        source: new VectorSource(),
        style: style
      });
      me.map.addLayer(vector);
      this.addIsochroneLayer(vector);
    },

    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneRoadNetworkLayer() {
      const me = this;
      const style = getIsochroneNetworkStyle();
      const vector = new VectorImageLayer({
        name: "isochroneRoadNetworkLayer",
        zIndex: 6,
        source: new VectorSource(),
        style: style
      });
      me.map.addLayer(vector);
      this.addIsochroneNetworkLayer(vector);
    },

    /**
     * Configure right-click for isochrone.
     */
    setUpCtxMenu() {
      if (this.contextmenu) {
        this.contextmenu.on("beforeopen", evt => {
          const features = this.map.getFeaturesAtPixel(evt.pixel, {
            layerFilter: candidate => {
              if (candidate.get("name") === "Isochrone Layer") {
                return true;
              }
              return false;
            }
          });
          if (features.length > 0) {
            this.contextmenu.extend([
              "-", // this is a separator
              {
                text: `<i class="fa fa-trash fa-1x" aria-hidden="true"></i>&nbsp;&nbsp${this.$t(
                  "map.contextMenu.deleteIsochrone"
                )}`,
                label: "deleteIsochrone",
                callback: () => {
                  const calculation = this.calculations.filter(
                    calculation =>
                      calculation.id === features[0].get("calculationNumber")
                  );
                  if (calculation[0]) {
                    this.deleteCalculation(calculation[0]);
                  }
                }
              }
            ]);
          }
        });
      }
    }
  },
  created() {
    this.init(this.$appConfig.componentData.isochrones);
  }
};
</script>
