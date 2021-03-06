<template>
  <v-flex>
    <v-card-text class="pr-16 pl-16 pt-0 pb-0">
      <v-divider></v-divider>
    </v-card-text>
    <v-subheader
      class="clickable"
      @click="isResultsElVisible = !isResultsElVisible"
    >
      <v-icon
        class="mr-2"
        :style="isResultsElVisible === true ? { color: '#30c2ff' } : {}"
        style="margin-right: 2px;"
        small
        >far fa-list-alt</v-icon
      >
      <h3>{{ $t("isochrones.results.title") }}</h3>
      <v-spacer></v-spacer>

      <v-btn
        v-show="isResultsElVisible === true && calculations.length > 1"
        small
        @click.stop="deleteAll"
        class="white--text"
        color="error"
      >
        <v-icon left>delete</v-icon>{{ $t("isochrones.results.deleteAll") }}
      </v-btn>
    </v-subheader>
    <v-layout>
      <v-flex xs12 class="mx-3" v-show="isResultsElVisible">
        <template v-for="calculation in calculations">
          <v-card
            class="mb-3 "
            :id="`result-${calculation.id}`"
            :key="calculation.id"
            :class="{
              'elevation-5': isCalculationActive(calculation)
            }"
          >
            <!-- Isochrone Nr -->
            <v-chip
              x-small
              dark
              label
              :color="isCalculationActive(calculation) ? '#30C2FF' : '#676767'"
              style="padding:5px;"
              class="isochrone-nr"
            >
              <span
                ><b>{{ calculation.id }}</b></span
              >
            </v-chip>
            <v-card-title class="pb-0 mb-0">
              <v-layout row wrap>
                <v-layout align-start justify-start>
                  <v-card-text class="pa-0 ma-0 ml-3">
                    <v-chip small class="mr-1 my-1">
                      <v-avatar left>
                        <v-icon small class="text-xs-center">{{
                          getRouteProfileIcon(calculation.routing_profile)
                        }}</v-icon>
                      </v-avatar>
                      {{
                        $t(`isochrones.options.${calculation.routing_profile}`)
                      }}
                    </v-chip>
                    <v-chip
                      v-if="calculation.scenario_id"
                      small
                      class="mr-0 my-1"
                    >
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <span v-on="on" class="chip-label-custom">
                            {{ scenarios[calculation.scenario_id].title }}
                          </span> </template
                        ><span>{{
                          scenarios[calculation.scenario_id].title
                        }}</span></v-tooltip
                      >
                    </v-chip>
                  </v-card-text>
                </v-layout>

                <v-layout row>
                  <v-spacer></v-spacer>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        small
                        v-on="on"
                        @click="toggleIsochroneWindow(calculation)"
                        :color="
                          isCalculationActive(calculation)
                            ? '#30C2FF'
                            : '#676767'
                        "
                        class="result-icons mr-1"
                        >fas fa-table</v-icon
                      >
                    </template>
                    <span>{{
                      isCalculationActive(calculation)
                        ? $t("isochrones.results.hideDataTooltip")
                        : $t("isochrones.results.showDataTooltip")
                    }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        small
                        v-on="on"
                        @click="showAdditionalLayerDialog(calculation)"
                        class="result-icons mr-1"
                        >fas fa-layer-group</v-icon
                      >
                    </template>
                    <span>{{ $t("isochrones.results.additionalLayers") }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        @click="showHideCalculation(calculation)"
                        small
                        v-on="on"
                        class="result-icons mr-1"
                        v-html="
                          calculation.isVisible
                            ? 'fas fa-eye-slash'
                            : 'fas fa-eye'
                        "
                      ></v-icon>
                    </template>
                    <span>{{
                      calculation.isVisible
                        ? $t("isochrones.results.hideResultsTooltip")
                        : $t("isochrones.results.showResultsTooltip")
                    }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        @click="toggleDownloadDialog(calculation)"
                        small
                        v-on="on"
                        class="result-icons mr-1"
                        >fas fa-download</v-icon
                      >
                    </template>
                    <span>{{ $t("isochrones.results.downloadTooltip") }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        @click="deleteCalculation(calculation)"
                        small
                        v-on="on"
                        class="result-icons delete-icon mr-6"
                      >
                        fas fa-trash-alt</v-icon
                      >
                    </template>
                    <span>{{
                      $t("isochrones.results.deleteCalcTooltip")
                    }}</span>
                  </v-tooltip>
                </v-layout>
              </v-layout>
              <v-card-text class="pr-0 pl-0 pt-0 pb-0">
                <v-divider></v-divider>

                <v-layout class="ml-0" row>
                  <v-chip small class="my-1 mr-1">
                    <v-avatar left>
                      <v-icon small class="text-xs-center">fas fa-clock</v-icon>
                    </v-avatar>
                    {{ calculation.time }}
                  </v-chip>

                  <v-chip small class="my-1 ">
                    <v-avatar left>
                      <v-icon small class="text-xs-center"
                        >fas fa-tachometer-alt</v-icon
                      >
                    </v-avatar>
                    {{ calculation.speed }}
                  </v-chip>
                  <v-spacer></v-spacer>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <div
                        v-if="
                          calculation.calculationMode === 'scenario' ||
                            calculation.calculationMode === 'comparison'
                        "
                        v-on="on"
                        @click="
                          toggleColorPickerDialog(calculation, 'scenario')
                        "
                        class="my-1 ml-1 mr-2 colorPalettePicker"
                        :style="{
                          backgroundImage: `linear-gradient(to right, ${getPaletteColor(
                            calculation,
                            'scenario'
                          )})`
                        }"
                      ></div>
                    </template>
                    <span>{{
                      $t(`map.tooltips.changeScenarioColorPalette`)
                    }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <div
                        v-if="
                          calculation.calculationMode === 'default' ||
                            calculation.calculationMode === 'comparison'
                        "
                        @click="toggleColorPickerDialog(calculation, 'default')"
                        v-on="on"
                        class="my-1 mr-2 colorPalettePicker"
                        :style="{
                          backgroundImage: `linear-gradient(to right, ${getPaletteColor(
                            calculation,
                            'default'
                          )})`
                        }"
                      ></div>
                    </template>
                    <span>{{
                      $t(`map.tooltips.changeDefaultColorPalette`)
                    }}</span>
                  </v-tooltip>
                </v-layout>
              </v-card-text>
            </v-card-title>
            <v-subheader
              class="clickable subheader mt-1 pb-1"
              @click="calculation.isExpanded = !calculation.isExpanded"
            >
              <v-icon
                small
                class="mr-2"
                v-html="
                  calculation.isExpanded
                    ? 'fas fa-chevron-down'
                    : 'fas fa-chevron-right'
                "
              ></v-icon>
              <v-tooltip
                :disabled="calculation.position === 'multiIsochroneCalculation'"
                open-delay="600"
                max-width="300"
                top
              >
                <template v-slot:activator="{ on }">
                  <h3 class="result-title" v-on="on">
                    {{
                      calculation.position === "multiIsochroneCalculation"
                        ? $t("isochrones.results.multiIsochroneHeader")
                        : calculation.position
                    }}
                  </h3>
                </template>
                <span>{{ calculation.position }}</span></v-tooltip
              >
            </v-subheader>

            <v-card-text class="pt-0 " v-show="calculation.isExpanded">
              <v-data-table
                :headers="headers"
                :items="calculation.data"
                class="elevation-1 subtitle-1"
                hide-default-footer
                light
              >
                <template v-slot:items="props">
                  <td>{{ props.item.type }}</td>
                  <td>{{ props.item.range }}</td>
                  <td>{{ props.item.area }}</td>
                </template>
                <template v-slot:item.visible="{ item }">
                  <v-switch
                    :input-value="item.isVisible"
                    primary
                    hide-details
                    @change="toggleIsochroneVisibility(item, calculation)"
                  ></v-switch>
                </template>
                <template v-slot:item.legend="{ item }">
                  <div
                    class="legend"
                    :style="{ backgroundColor: item.color }"
                  ></div>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </template>
      </v-flex>
      <confirm ref="confirm"></confirm>
      <!-- DIALOG BOXES FOR ISOCHRONE RESULTS -->
      <download
        :visible="downloadDialogState"
        :calculation="selectedCalculation"
        @close="downloadDialogState = false"
      ></download>
      <additional-layers
        :visible="additionalLayersDialogState"
        :calculation="selectedCalculation"
        @close="additionalLayersDialogState = false"
      ></additional-layers>
      <isochrone-color-picker
        :visible="isochroneColorPickerState"
        :calculation="activeCalculation"
        :selectedMode="activeCalculationMode"
        @close="isochroneColorPickerState = false"
      ></isochrone-color-picker>
    </v-layout>
  </v-flex>
</template>
<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import Download from "./IsochronesDownload";
import AdditionalLayers from "./IsochronesAdditionalLayers";
import IsochroneColorPicker from "./IsochroneColorPicker";
import { Isochrones } from "../../mixins/Isochrones";

export default {
  mixins: [Isochrones],
  components: {
    download: Download,
    additionalLayers: AdditionalLayers,
    IsochroneColorPicker
  },
  data() {
    return {
      downloadDialogState: false,
      additionalLayersDialogState: false,
      selectedCalculation: null,
      isochroneColorPickerState: false,
      activeCalculation: null, // for color palette selection
      activeCalculationMode: null, // for color palette selection
      isResultsElVisible: true
    };
  },

  methods: {
    ...mapActions("isochrones", {
      removeCalculation: "removeCalculation",
      showIsochroneWindow: "showIsochroneWindow"
    }),
    ...mapMutations("isochrones", {
      toggleIsochroneFeatureVisibility: "TOGGLE_ISOCHRONE_FEATURE_VISIBILITY",
      toggleIsochroneCalculationVisibility:
        "TOGGLE_ISOCHRONE_CALCULATION_VISIBILITY",
      toggleThematicDataVisibility: "TOGGLE_THEMATIC_DATA_VISIBILITY"
    }),
    toggleIsochroneVisibility(feature, calculation) {
      //Get all visible calculation
      const visibleFeatures = calculation.data.filter(
        feature => feature.isVisible === true
      );

      let isNetworkVisible = false;
      Object.keys(calculation.additionalData).forEach(key => {
        if (calculation.additionalData[key].state === true) {
          isNetworkVisible = true;
        }
      });

      //If user has turned off other features, hide the result
      if (
        !isNetworkVisible &&
        visibleFeatures.length === 1 &&
        visibleFeatures[0].id === feature.id &&
        visibleFeatures[0].isVisible === true
      ) {
        this.showHideCalculation(calculation);
      } else {
        this.toggleIsochroneFeatureVisibility(feature);
      }

      if (calculation.isVisible === false && feature.isVisible === true) {
        calculation.isVisible = true;
      }
    },
    toggleDownloadDialog(calculation) {
      this.downloadDialogState = true;
      this.selectedCalculation = calculation;
    },
    showHideNetworkData(calculation) {
      //Check if road netowrk is visible. Is so remove all features from map.
      const roadNetworkData = calculation.additionalData;
      for (let type in roadNetworkData) {
        // type can be 'Deafult' or 'Input'
        const state = roadNetworkData[type].state;
        const roadNetworkSource = this.isochroneRoadNetworkLayer.getSource();
        const features = roadNetworkData[type].features;
        if (state === true && calculation.isVisible === true) {
          features.forEach(feature => {
            if (roadNetworkSource.hasFeature(feature)) {
              roadNetworkSource.removeFeature(feature);
            }
          });
        } else if (state === true && calculation.isVisible === false) {
          features.forEach(feature => {
            roadNetworkSource.addFeature(feature);
          });
        }
      }
    },
    showHideIsochroneOverlayFeatures(calculation) {
      const id = calculation.id;
      const isVisible = !calculation.isVisible;
      this.isochroneOverlayLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (feature.get("calculationNumber") === id) {
            feature.set("isVisible", isVisible);
          }
        });
    },
    showHideCalculation(calculation) {
      const me = this;

      me.showHideNetworkData(calculation);
      me.showHideIsochroneOverlayFeatures(calculation);
      me.toggleIsochroneCalculationVisibility(calculation);
    },
    showAdditionalLayerDialog(calculation) {
      this.additionalLayersDialogState = true;
      this.selectedCalculation = calculation;
    },
    isCalculationActive(calculation) {
      if (
        this.selectedThematicData &&
        this.isThematicDataVisible &&
        calculation &&
        this.selectedThematicData.calculationId === calculation.id
      ) {
        return true;
      } else {
        return false;
      }
    },
    getRouteProfileIcon(route) {
      const routingName = route.split("_")[0];
      //Edge-case
      if (route.includes("walking_wheelchair")) {
        return this.routeIcons["walking_wheelchair"];
      }
      return this.routeIcons[routingName];
    },
    toggleIsochroneWindow(calculation) {
      if (this.isCalculationActive(calculation)) {
        // Hide
        this.isochroneLayer
          .getSource()
          .getFeatures()
          .forEach(f => {
            f.set("highlightFeature", false);
          });
        this.toggleThematicDataVisibility(false);
      } else {
        // Show
        this.showIsochroneWindow({
          id: calculation.id,
          calculationType: calculation.calculationType
        });
      }
    },
    deleteAll() {
      this.$refs.confirm
        .open(
          this.$t("isochrones.deleteTitle"),
          this.$t("isochrones.deleteAllMessage"),
          { color: "green" }
        )
        .then(confirm => {
          if (confirm) {
            this.calculations.forEach(calculation => {
              this.removeCalculation(calculation);
            });
          }
        });
    },
    getPaletteColor(calculation, mode) {
      const colorKey = `${mode}ColorPalette`;
      return Object.values(this.colors[calculation[colorKey]]).toString();
    },
    toggleColorPickerDialog(calculation, mode) {
      this.isochroneColorPickerState = true;
      this.activeCalculation = calculation;
      this.activeCalculationMode = mode;
    }
  },
  computed: {
    ...mapGetters("isochrones", {
      calculations: "calculations",
      scenarios: "scenarios",
      routeIcons: "routeIcons",
      isochroneLayer: "isochroneLayer",
      isochroneRoadNetworkLayer: "isochroneRoadNetworkLayer",
      isochroneOverlayLayer: "isochroneOverlayLayer",
      selectedThematicData: "selectedThematicData",
      isThematicDataVisible: "isThematicDataVisible",
      colors: "colors"
    }),
    headers() {
      return [
        {
          text: this.$t("isochrones.results.table.type"),
          value: "type",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.range"),
          value: "range",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.area"),
          value: "area",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.visible"),
          value: "visible",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.legend"),
          value: "legend",
          sortable: false
        }
      ];
    }
  }
};
</script>
<style lang="css">
.result-icons {
  color: "#4A4A4A";
  cursor: pointer;
}
.result-icons:hover {
  color: #30c2ff;
}
.delete-icon:hover {
  color: #ff6060;
}
.isochrone-nr {
  position: absolute;
}
.v-data-table td,
.v-data-table th {
  padding: 0 5px;
}
.v-data-table th {
  font-size: 14px;
}
.v-data-table td {
  font-size: 13px;
}
.legend {
  height: 24px;
  border-radius: 7px;
}

.colorPalettePicker {
  height: 24px;
  border-radius: 7px;
  width: 50px;
  cursor: pointer;
}

.activeIcon {
  color: #30c2ff;
}
.v-input--selection-controls {
  margin-top: 0px;
  padding-top: 0px;
}

.subheader {
  height: 25px;
}

.v-chip--label {
  border-radius: 0px 8px 8px 0px !important;
}

.result-title {
  display: inline-block;
  width: 265px;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chip-label-custom {
  display: block;
  width: 66px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
