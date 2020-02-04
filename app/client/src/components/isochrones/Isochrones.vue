<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <!-- ISOCHRONES  -->
      <template>
        <v-subheader>
          <span class="title">{{ $t("isochrones.title") }}</span>
        </v-subheader>
        <isochrone-type />

        <isochrone-start-single v-if="options.calculationType === 'single'" />
        <isochrone-start-multiple
          v-if="options.calculationType === 'multiple'"
        />
        <isochrone-options />
        <isochrone-results />
      </template>
      <!-- -- -->
    </v-card>
  </v-flex>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";

//Child components
import IsochroneOptions from "./IsochroneOptions";
import IsochroneResults from "./IsochroneResults";
import IsochroneType from "./IsochroneType";
import IsochroneStartSingle from "./IsochroneStartSingle";
import IsochroneStartMultiple from "./IsochroneStartMultiple";

import OlStyleDefs from "../../style/OlStyleDefs";

//Store imports
import { mapGetters, mapMutations } from "vuex";

//Ol imports
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import VectorImageLayer from "ol/layer/VectorImage";

export default {
  mixins: [Mapable],
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
      options: "options"
    })
  },
  methods: {
    ...mapMutations("isochrones", {
      init: "INIT",
      addStyleInCache: "ADD_STYLE_IN_CACHE",
      addIsochroneLayer: "ADD_ISOCHRONE_LAYER",
      addIsochroneNetworkLayer: "ADD_ISOCHRONE_ROAD_NETWORK_LAYER"
    }),

    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.createIsochroneLayer();
      this.createIsochroneRoadNetworkLayer();
    },

    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneLayer() {
      const me = this;
      const style = OlStyleDefs.getIsochroneStyle(
        me.styleData,
        me.addStyleInCache
      );
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
      const style = OlStyleDefs.getIsochroneNetworkStyle();
      const vector = new VectorImageLayer({
        name: "isochroneRoadNetworkLayer",
        zIndex: 6,
        source: new VectorSource(),
        style: style
      });
      me.map.addLayer(vector);
      this.addIsochroneNetworkLayer(vector);
    }
  },
  created() {
    this.init(this.$appConfig.componentData.isochrones);
  }
};
</script>
