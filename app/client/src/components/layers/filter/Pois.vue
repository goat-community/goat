<template>
  <div>
    <template v-if="timeBasedCalculations === 'yes'">
      <v-switch
        class="subtitle-2 mt-4 mb-0 pb-0"
        dense
        v-model="showTimeFilters"
        @change="toggleTimeFilter"
        :label="$t(`poisFilter.showTimeFilter`)"
      ></v-switch>
      <v-select
        v-if="showTimeFilters"
        class="mt-1 pt-1"
        item-value="value"
        :items="timeFilter.day.values"
        v-model="dayFilter"
        prepend-icon="today"
        :label="$t('poisFilter.selectDayLabel')"
      >
        <template slot="selection" slot-scope="{ item }">
          {{ $t(`poisFilter.daysOfWeek.${item.display}`) }}
        </template>
        <template slot="item" slot-scope="{ item }">
          {{ $t(`poisFilter.daysOfWeek.${item.display}`) }}
        </template>
      </v-select>

      <v-menu
        v-if="showTimeFilters"
        class="mt-0 pt-0"
        ref="menu"
        v-model="timeSelectMenu"
        :close-on-content-click="false"
        :nudge-right="40"
        :return-value.sync="hourFilter"
        transition="scale-transition"
        offset-y
      >
        <template v-slot:activator="{ on }">
          <v-text-field
            v-model="hourFilter"
            :label="$t('poisFilter.selectHourLabel')"
            prepend-icon="access_time"
            readonly
            v-on="on"
          ></v-text-field>
        </template>
        <v-time-picker
          v-if="timeSelectMenu"
          v-model="hourFilter"
          format="24hr"
          color="green"
          full-width
          @click:minute="$refs.menu.save(hourFilter)"
        ></v-time-picker>
      </v-menu>
      <v-divider class="mx-2"></v-divider>
    </template>

    <v-treeview
      v-model="selectedPois"
      :open="open"
      :items="allPois"
      ref="poisTree"
      activatable
      open-on-click
      dense
      selectable
      rounded
      return-object
      item-key="name"
      item-disabled="locked"
      selected-color="green"
      active-class="grey lighten-4 indigo--text "
      on-icon="check_box"
      off-icon="check_box_outline_blank"
      indeterminate-icon="indeterminate_check_box"
      @input="treeViewChanged"
    >
      <template v-slot:prepend="{ item }">
        <img v-if="item.icon" class="pois-icon" :src="getPoisIconUrl(item)" />
      </template>
      <template v-slot:label="{ item }">
        <div class="tree-label-custom">{{ getDisplayName(item) }}</div>
      </template>
      <template v-slot:append="{ item }">
        <template v-if="item.icon">
          <v-tooltip top>
            <template v-slot:activator="{ on }">
              <v-icon
                @click="toggleHeatmapDialog(item)"
                small
                v-on="on"
                class="arrow-icons mr-1"
              >
                fas fa-cog
              </v-icon>
            </template>
            <span>{{ $t("appBar.filter.poisSettings.buttonTooltip") }}</span>
          </v-tooltip>
        </template>
      </template>
    </v-treeview>
    <heatmap-options
      :visible="showHeatmapOptionsDialog"
      :selectedAmenity="selectedAmenity"
      @updated="updateHeatmapLayerViewParams"
      @close="showHeatmapOptionsDialog = false"
    />
  </div>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import { getAllChildLayers } from "../../../utils/Layer";
import { mapGetters, mapActions } from "vuex";
import { mapFields } from "vuex-map-fields";
import { mapMutations } from "vuex";
import HeatmapOptions from "./HeatmapOptions";

export default {
  mixins: [Mapable],
  components: {
    "heatmap-options": HeatmapOptions
  },
  data() {
    return {
      timeBasedCalculations: this.$appConfig.componentConf.pois.filters
        .timeBasedCalculations,
      timeSelectMenu: false,
      showTimeFilters: false,
      open: [],
      heatmapLayers: [],
      poisLayer: null,
      showHeatmapOptionsDialog: false,
      selectedAmenity: {}
    };
  },

  methods: {
    ...mapActions("pois", {
      updateSelectedPoisForThematicData: "updateSelectedPoisForThematicData"
    }),
    ...mapActions("isochrones", {
      countStudyAreaPois: "countStudyAreaPois"
    }),
    getPoisIconUrl(item) {
      const images = require.context(
        "../../../assets/img/pois/",
        false,
        /\.png$/
      );
      return images("./" + item.icon + ".png");
    },

    onMapBound() {
      const me = this;
      const map = me.map;
      const heatmapLayerNames = ["walkability", "walkabilityPopulation"];
      const poisLayerName = "pois";

      const allLayers = getAllChildLayers(map);
      allLayers.forEach(layer => {
        const layerName = layer.get("name");
        if (heatmapLayerNames.includes(layerName)) {
          me.heatmapLayers.push(layer);
        }
        if (layerName === poisLayerName) {
          me.poisLayer = layer;
        }
      });
    },
    updateHeatmapLayerViewParams() {
      const me = this;
      const selectedPois = me.selectedPois;

      const heatmapViewParams = selectedPois.reduce((filtered, item) => {
        const { value, weight, sensitivity } = item;
        if (value != "undefined" && weight != undefined) {
          filtered.push({
            [`${value}`]: { sensitivity: sensitivity, weight: weight }
          });
        }
        return filtered;
      }, []);

      me.heatmapLayers.forEach(layer => {
        const viewparams = JSON.stringify(heatmapViewParams);
        layer.getSource().updateParams({
          viewparams: `amenities:'${btoa(viewparams)}'`
        });
        if (layer.getVisible() === true && heatmapViewParams.length === 0) {
          this.toggleSnackbar({
            type: "error",
            message: "selectAmenities",
            timeout: 60000,
            state: true
          });
        } else {
          this.toggleSnackbar({
            type: "error",
            message: "selectAmenities",
            state: false,
            timeout: 0
          });
        }

        layer.getSource().refresh();
      });
    },
    updatePoisLayerViewParams(selectedPois) {
      const me = this;
      if (me.poisLayer) {
        const viewParams = selectedPois.reduce((filtered, item) => {
          const { value } = item;
          if (value != "undefined") {
            filtered.push(value);
          }
          return filtered;
        }, []);

        let params = `amenities:'${btoa(
          viewParams.toString()
        )}';routing_profile:'${me.activeRoutingProfile}';userid:${me.userId};`;

        if (this.timeBasedCalculations === "yes") {
          params += `d:${me.getSelectedDay};h:${me.getSelectedHour};m:${me.getSelectedMinutes};`;
        }

        me.poisLayer.getSource().updateParams({
          viewparams: params
        });
      }
    },
    toggleHeatmapDialog(amenity) {
      this.selectedAmenity = amenity;
      this.showHeatmapOptionsDialog = true;
    },
    getDisplayName(item) {
      let value;
      if (item.value) {
        //Display name for amenities
        value = this.$t(`pois.${item.value}`);
      } else {
        //Display name from categories
        value = this.$t(`pois.${item.categoryValue}`);
      }
      return value;
    },
    toggleTimeFilter() {
      if (this.showTimeFilters === false) {
        this.dayFilter = "";
        this.hourFilter = null;
        this.toggleNodeState({
          excluded: this.disabledPoisOnTimeFilter,
          nodeState: "deactivate"
        });
      } else {
        //Disable pois icons which are excluded from time filter
        this.toggleNodeState({
          excluded: this.disabledPoisOnTimeFilter,
          nodeState: "activate"
        });
      }
    },
    ...mapMutations("pois", {
      toggleNodeState: "TOGGLE_NODE_STATE",
      init: "INIT"
    }),
    toggleRoutingFilter(newValue, oldValue) {
      const oldFiter = this.disabledPoisOnRoutingProfile[oldValue];
      if (oldFiter) {
        this.toggleNodeState({
          excluded: oldFiter,
          nodeState: "deactivate"
        });
      }
      const newFilter = this.disabledPoisOnRoutingProfile[newValue];
      if (newFilter) {
        this.toggleNodeState({
          excluded: newFilter,
          nodeState: "activate"
        });
      }
    },
    treeViewChanged() {
      this.selectedPois = this.selectedPois.filter(x => x.locked != true);
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  watch: {
    selectedPois: function() {
      const me = this;
      if (me.selectedPois.length > 0 && me.poisLayer.getVisible() === false) {
        me.poisLayer.setVisible(true);
      }
      me.updateSelectedPoisForThematicData(me.selectedPois);
      me.updateHeatmapLayerViewParams();
      me.updatePoisLayerViewParams(me.selectedPois);
      me.countStudyAreaPois();
    },
    activeRoutingProfile: function(newValue, oldValue) {
      if (this.timeBasedCalculations === "yes") {
        this.toggleRoutingFilter(newValue, oldValue);
      }
      this.updatePoisLayerViewParams(this.selectedPois);
    },
    dayFilter: function() {
      this.updatePoisLayerViewParams(this.selectedPois);
    },
    hourFilter: function() {
      this.updatePoisLayerViewParams(this.selectedPois);
    }
  },
  computed: {
    ...mapGetters("pois", {
      allPois: "allPois",
      timeFilter: "timeFilter",
      disabledPoisOnTimeFilter: "disabledPoisOnTimeFilter",
      disabledPoisOnRoutingProfile: "disabledPoisOnRoutingProfile"
    }),
    ...mapGetters("isochrones", {
      options: "options",
      activeRoutingProfile: "activeRoutingProfile"
    }),
    ...mapGetters("user", { userId: "userId" }),
    ...mapFields("pois", {
      dayFilter: "timeFilter.day.active",
      hourFilter: "timeFilter.hour",
      selectedPois: "selectedPois"
    }),
    getSelectedDay() {
      return this.dayFilter ? this.dayFilter : 9999;
    },
    getSelectedHour() {
      return this.hourFilter !== null ? this.hourFilter.split(":")[0] : 9999;
    },
    getSelectedMinutes() {
      return this.hourFilter !== null ? this.hourFilter.split(":")[1] : 9999;
    }
  },
  created() {
    this.init(this.$appConfig.componentData.pois);
    this.toggleRoutingFilter(this.activeRoutingProfile, null);
  }
};
</script>
<style lang="css">
.arrow-icons {
  color: "#4A4A4A";
}
.arrow-icons:hover {
  cursor: pointer;
  color: #30c2ff;
}

.pois-icon {
  margin-bottom: 15px;
}
.v-treeview-node--leaf {
  margin-left: 30px;
}
.v-treeview-node__content,
.v-treeview-node__label {
  flex-shrink: 1;
}
.tree-label-custom {
  display: block;
  width: 150px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
}
.v-treeview-node--leaf > .v-treeview-node__root {
  padding-left: 5px;
  padding-right: 4px;
}
</style>
