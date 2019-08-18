<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <!-- THEMATIC DATA -->
      <template v-if="isThematicDataVisible === true">
        <v-layout>
          <v-btn
            text
            icon
            class="mt-1 ml-1"
            light
            @click="toggleThematicDataVisibility(false)"
          >
            <v-icon color="rgba(0,0,0,0.54)">fas fa-arrow-left</v-icon>
          </v-btn>
          <v-subheader class="ml-1 pl-0">
            <span class="title">Thematic Data</span>
          </v-subheader>
        </v-layout>
        <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
          <v-divider></v-divider>
        </v-card-text>
        <isochrone-thematic-data />
      </template>

      <!-- ISOCHRONES  -->
      <template v-else>
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
import IsochronThematicData from "./IsochronesThematicData";
import IsochroneType from "./IsochroneType";
import IsochroneStartSingle from "./IsochroneStartSingle";
import IsochroneStartMultiple from "./IsochroneStartMultiple";

import OlStyleDefs from "../../style/OlStyleDefs";

//Store imports
import { mapGetters, mapMutations } from "vuex";

//Ol imports
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";

export default {
  mixins: [Mapable],
  components: {
    "isochrone-options": IsochroneOptions,
    "isochrone-results": IsochroneResults,
    "isochrone-thematic-data": IsochronThematicData,
    "isochrone-type": IsochroneType,
    "isochrone-start-single": IsochroneStartSingle,
    "isochrone-start-multiple": IsochroneStartMultiple
  },
  computed: {
    ...mapGetters("isochrones", {
      styleData: "styleData",
      isThematicDataVisible: "isThematicDataVisible",
      options: "options"
    })
  },
  methods: {
    ...mapMutations("isochrones", {
      addStyleInCache: "ADD_STYLE_IN_CACHE",
      addIsochroneLayer: "ADD_ISOCHRONE_LAYER",
      toggleThematicDataVisibility: "TOGGLE_THEMATIC_DATA_VISIBILITY"
    }),
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.createIsochroneLayer();
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
        zIndex: 2,
        source: new VectorSource(),
        style: style
      });
      me.map.addLayer(vector);
      this.addIsochroneLayer(vector);
    }
  }
};
</script>
