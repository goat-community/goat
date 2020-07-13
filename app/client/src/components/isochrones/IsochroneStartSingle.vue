<template>
  <v-flex xs12>
    <v-card-text class="pr-16 pl-16 pt-0 pb-0">
      <v-divider></v-divider>
    </v-card-text>
    <v-subheader
      @click="isIsochroneStartElVisible = !isIsochroneStartElVisible"
      class="clickable pb-0 mb-0"
    >
      <v-icon
        :class="{
          activeIcon: isIsochroneStartElVisible,
          'mr-3': true
        }"
        style="margin-right: 2px;"
        small
        >fas fa-map-marker-alt</v-icon
      >
      <h3>{{ $t("isochrones.single.title") }}</h3>
    </v-subheader>
    <v-card-text v-show="isIsochroneStartElVisible" class="pt-0 pb-1 mt-0 mb-1">
      <v-layout row>
        <v-flex xs9>
          <v-autocomplete
            solo
            v-model="model"
            :items="items"
            :loading="isLoading"
            :disabled="isBusy"
            :label="$t('isochrones.single.searchBox')"
            :search-input.sync="search"
            item-text="DisplayName"
            append-icon=""
            clear-icon="close"
            @click:clear="clearSearch"
            @change="selectSearchStartingPoint"
            clearable
            item-value="osm_id"
            hide-details
            hide-selected
            hide-no-data
            prepend-inner-icon="search"
            return-object
            class="ml-3 mt-1"
            :menu-props="{ maxHeight: 600 }"
          ></v-autocomplete>
        </v-flex>
        <v-flex xs3>
          <span v-if="!isBusy">
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn
                  outlined
                  fab
                  v-on="on"
                  class="ml-4"
                  depressed
                  text
                  @click="registerMapClick"
                >
                  <v-icon color="#30C2FF">fas fa-map-marker-alt</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("isochrones.single.startTooltip") }}</span>
            </v-tooltip>
          </span>

          <span v-if="isBusy">
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn
                  fab
                  dark
                  v-on="on"
                  class="ml-4 elevation-0"
                  color="red"
                  @click="stopIsochroneCalc"
                >
                  <v-icon color="white">close</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("isochrones.stopIsochroneCalc") }}</span>
            </v-tooltip>
          </span>
        </v-flex>
      </v-layout>
    </v-card-text>
    <v-progress-linear
      v-if="isBusy"
      indeterminate
      height="1"
      class="mx-0 pb-0"
      color="green"
    ></v-progress-linear>
  </v-flex>
</template>
<script>
import { EventBus } from "../../EventBus";
import { Mapable } from "../../mixins/Mapable";
import { KeyShortcuts } from "../../mixins/KeyShortcuts";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";

//Store imports
import { mapGetters, mapActions, mapMutations } from "vuex";

import { unByKey } from "ol/Observable";
import axios from "axios";

//Other imports
import { debounce } from "../../utils/Helpers";

//Ol imports
import { transform, transformExtent } from "ol/proj.js";

export default {
  mixins: [InteractionsToggle, Mapable, KeyShortcuts],
  data: () => ({
    interactionType: "isochrone-single-interaction",
    descriptionLimit: 30,
    entries: [],
    model: null,
    search: null,
    isLoading: false,
    mapClickListener: null,
    isIsochroneStartElVisible: true
  }),
  computed: {
    ...mapGetters("map", {
      messages: "messages"
    }),
    ...mapGetters("isochrones", {
      isBusy: "isBusy",
      cancelReq: "cancelReq"
    }),
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
        const DisplayName =
          entry.display_name.length > this.descriptionLimit
            ? entry.display_name.slice(0, this.descriptionLimit) + "..."
            : entry.display_name;

        return Object.assign({}, entry, { DisplayName });
      });
    }
  },
  methods: {
    ...mapActions("isochrones", { calculateIsochrone: "calculateIsochrone" }),
    ...mapMutations("isochrones", { updatePosition: "UPDATE_POSITION" }),
    ...mapMutations("map", {
      startHelpTooltip: "START_HELP_TOOLTIP",
      stopHelpTooltip: "STOP_HELP_TOOLTIP"
    }),
    registerMapClick() {
      const me = this;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", me.interactionType);

      me.mapClickListener = me.map.once("singleclick", me.onMapClick);
      me.startHelpTooltip(this.$t("map.tooltips.clickForCalculation"));
      me.map.getTarget().style.cursor = "pointer";
      if (this.addKeyupListener) {
        this.addKeyupListener();
      }
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
        placeName: ""
      });
      //Start Isochrone Calculation
      me.calculateIsochrone();
      me.clear();
    },
    selectSearchStartingPoint() {
      const me = this;
      if (!this.search || !this.model) return;
      const lat = parseFloat(this.model.lat);
      const lon = parseFloat(this.model.lon);

      me.updatePosition({
        coordinate: [lon, lat],
        placeName: this.model.DisplayName
      });
      me.calculateIsochrone();
    },

    clear() {
      const me = this;
      if (me.mapClickListener) {
        unByKey(me.mapClickListener);
      }

      me.stopHelpTooltip();
      me.map.getTarget().style.cursor = "";
      EventBus.$emit("ol-interaction-stoped", me.interactionType);
    },
    /**
     * stops single isochrone interaction
     */
    stop() {
      const me = this;
      me.clear();
    },
    stopIsochroneCalc() {
      if (this.cancelReq instanceof Function) {
        this.cancelReq("cancelled");
      }
    },
    clearSearch() {
      this.entries = [];
      this.count = 0;
    }
  },
  watch: {
    search: debounce(function() {
      // Items have already been requested
      if (this.isLoading || !this.search) return;
      this.isLoading = true;
      if (!this.studyAreaBbox) return;
      axios
        .get(
          `${this.searchUrl}autocomplete.php?key=${this.searchKey}&q=${this.search}
            &viewbox=${this.studyAreaBbox}&bounded=1`
        )
        .then(response => {
          this.count = response.data.length;
          this.entries = response.data;
          this.isLoading = false;
        })
        .catch(() => {
          this.isLoading = false;
        });
    }, 600)
  },
  mounted() {
    const me = this;
    me.searchUrl = process.env.VUE_APP_SEARCH_URL;
    me.searchKey = process.env.VUE_APP_SEARCH_KEY;
    this.studyAreaBbox = transformExtent(
      this.$appConfig.map.extent,
      "EPSG:3857",
      "EPSG:4326"
    );
  }
};
</script>
<style lang="css" scoped>
.activeIcon {
  color: #30c2ff;
}
</style>
