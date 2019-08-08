<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <!-- THEMATIC DATA -->
      <template v-if="isThematicDataVisible === true">
        <v-layout>
          <v-btn
            text
            icon
            small
            class="mt-1"
            light
            @click="toggleThematicDataVisibility(false)"
          >
            <v-icon color="rgba(0,0,0,0.54)">fas fa-arrow-left</v-icon>
          </v-btn>
          <v-subheader class="ml- pl-0">
            <span class="title">Thematic Data</span>
          </v-subheader>
        </v-layout>
        <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
          <v-divider></v-divider>
        </v-card-text>
        <isochrone-thematic-data />
      </template>

      <!-- ISOCHRONE OPTIONS AND RESULTS  -->
      <template v-else>
        <v-subheader>
          <span class="title">{{ $t("isochrones.title") }}</span>
        </v-subheader>

        <v-card-text class="pr-16 pl-16 pt-0 pb-0">
          <v-divider></v-divider>
        </v-card-text>
        <v-card-text>
          <v-layout row>
            <v-flex xs9>
              <v-autocomplete
                solo
                v-model="model"
                :items="items"
                :loading="isLoading"
                label="Search Road"
                :search-input.sync="search"
                item-text="Description"
                append-icon=""
                item-value="API"
                hide-details
                hide-no-data
                prepend-inner-icon="search"
                return-object
                class="ml-3 mt-1"
              ></v-autocomplete>
            </v-flex>
            <v-flex xs3>
              <v-btn
                outlined
                fab
                class="ml-4"
                rounded
                text
                @click="registerMapClick"
              >
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
import { Mapable } from "../../mixins/Mapable";
import { EventBus } from "../../EventBus";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";
//Child components
import IsochroneOptions from "./IsochroneOptions";
import IsochroneResults from "./IsochroneResults";
import IsochronThematicData from "./IsochronesThematicData";

import OlStyleDefs from "../../style/OlStyleDefs";

//Store imports
import { mapGetters, mapActions, mapMutations } from "vuex";

//Ol imports
import { transform } from "ol/proj.js";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import { unByKey } from "ol/Observable";

export default {
  mixins: [InteractionsToggle, Mapable],
  components: {
    "isochrone-options": IsochroneOptions,
    "isochrone-results": IsochroneResults,
    "isochrone-thematic-data": IsochronThematicData
  },
  data: () => ({
    interactionType: "isochrone-interaction",
    clicked: false,
    isStartPointElVisible: true,
    isOptionsElVisible: true,
    isResultsElVisible: true,
    //Road Search
    descriptionLimit: 60,
    entries: [],
    model: null,
    search: null,
    isLoading: false,
    mapClickListener: null
  }),
  computed: {
    ...mapGetters("isochrones", {
      styleData: "styleData",
      isThematicDataVisible: "isThematicDataVisible"
    }),
    ...mapGetters("map", { messages: "messages" }),
    fields() {
      if (!this.model) return [];

      return Object.keys(this.model).map(key => {
        return {
          key,
          value: this.model[key] || "n/a"
        };
      });
    },
    items() {
      return this.entries.map(entry => {
        const Description =
          entry.Description.length > this.descriptionLimit
            ? entry.Description.slice(0, this.descriptionLimit) + "..."
            : entry.Description;

        return Object.assign({}, entry, { Description });
      });
    }
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
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.createIsochroneLayer();
    },
    registerMapClick() {
      const me = this;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", me.interactionType);

      me.mapClickListener = me.map.once("singleclick", me.onMapClick);
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
      me.clear();
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
    },

    clear() {
      const me = this;
      if (me.mapClickListener) {
        unByKey(me.mapClickListener);
      }
      me.stopHelpTooltip();
      me.map.getTarget().style.cursor = "";
    }
  },
  watch: {
    search(val) {
      console.log(val);
      // Items have already been loaded
      if (this.items.length > 0) return;
      // Items have already been requested
      if (this.isLoading) return;

      this.isLoading = true;

      // Lazily load input items
      fetch("")
        .then(res => res.json())
        .then(res => {
          const { count, entries } = res;
          this.count = count;
          this.entries = entries;
        })
        .catch(err => {
          console.log(err);
        })
        .finally(() => (this.isLoading = false));
    }
  }
};
</script>
<style lang="css" scoped>
.activeIcon {
  color: #30c2ff;
}
</style>
