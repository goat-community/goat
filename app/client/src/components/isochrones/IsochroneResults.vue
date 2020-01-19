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
    </v-subheader>
    <v-layout>
      <v-flex xs12 class="mx-3" v-show="isResultsElVisible">
        <template v-for="calculation in calculations">
          <v-card class="mb-3 " :key="calculation.id">
            <!-- Isochrone Nr -->
            <div class="isochrone-nr">{{ calculation.id }}</div>
            <v-card-title class="pb-0 mb-0">
              <v-layout row wrap>
                <v-layout align-start justify-start>
                  <v-card-text class="pa-0 ma-0 ml-3">
                    <v-icon small class="mr-1 text-xs-center"
                      >fas fa-clock</v-icon
                    >
                    <span class="subtitle-2 text-xs-center">{{
                      calculation.time
                    }}</span>
                    <v-icon small class="ml-2 mr-1 "
                      >fas fa-tachometer-alt</v-icon
                    >
                    <span class="subtitle-2 text-xs-center">{{
                      calculation.speed
                    }}</span>
                  </v-card-text>
                </v-layout>

                <v-layout row>
                  <v-spacer></v-spacer>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        small
                        v-on="on"
                        @click="showAdditionalLayerDialog(calculation)"
                        class="result-icons mr-2"
                        >fas fa-layer-group</v-icon
                      >
                    </template>
                    <span>{{ $t("isochrones.results.additionalLayers") }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        @click="showPoisTable(calculation)"
                        small
                        v-on="on"
                        class="result-icons mr-2"
                        >fas fa-table</v-icon
                      >
                    </template>
                    <span>{{ $t("isochrones.results.showDataTooltip") }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        @click="showHideCalculation(calculation)"
                        small
                        v-on="on"
                        class="result-icons mr-2"
                        v-html="
                          calculation.isVisible
                            ? 'fas fa-eye-slash'
                            : 'fas fa-eye'
                        "
                      ></v-icon>
                    </template>
                    <span>{{
                      $t("isochrones.results.toggleVisibilityTooltip")
                    }}</span>
                  </v-tooltip>

                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-icon
                        @click="toggleDownloadDialog(calculation)"
                        small
                        v-on="on"
                        class="result-icons mr-2"
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
                        class="result-icons mr-6"
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
              </v-card-text>
            </v-card-title>
            <v-subheader
              class="clickable subheader mt-1"
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
              <h3>
                {{
                  calculation.position === "multiIsochroneCalculation"
                    ? $t("isochrones.results.multiIsochroneHeader")
                    : calculation.position
                }}
              </h3>
            </v-subheader>
            <v-subheader
              @click="calculation.isExpanded = !calculation.isExpanded"
              class="clickable subheader subtitle-2"
            >
              <span
                >{{ $t("isochrones.options.routingProfile") }} :
                {{
                  $te(`isochrones.options.${calculation.routing_profile}`)
                    ? $t(`isochrones.options.${calculation.routing_profile}`)
                    : calculation.routing_profile
                }}</span
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
                    @change="toggleIsochroneFeatureVisibility(item)"
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
    </v-layout>
  </v-flex>
</template>
<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import Confirm from "../core/Confirm";
import Download from "./IsochronesDownload";
import AdditionalLayers from "./IsochronesAdditionalLayers";
import IsochroneUtils from "../../utils/IsochroneUtils";

export default {
  components: {
    confirm: Confirm,
    download: Download,
    additionalLayers: AdditionalLayers
  },
  data() {
    return {
      downloadDialogState: false,
      additionalLayersDialogState: false,
      selectedCalculation: null,
      isResultsElVisible: true
    };
  },

  methods: {
    ...mapActions("isochrones", {
      removeCalculation: "removeCalculation",
      setSelectedThematicData: "setSelectedThematicData"
    }),
    ...mapMutations("isochrones", {
      toggleIsochroneFeatureVisibility: "TOGGLE_ISOCHRONE_FEATURE_VISIBILITY",
      toggleIsochroneCalculationVisibility:
        "TOGGLE_ISOCHRONE_CALCULATION_VISIBILITY",
      toggleThematicDataVisibility: "TOGGLE_THEMATIC_DATA_VISIBILITY"
    }),
    deleteCalculation(calculation) {
      this.$refs.confirm
        .open(
          this.$t("isochrones.deleteTitle"),
          this.$t("isochrones.deleteMessage") + " " + calculation.id + " ?",
          { color: "green" }
        )
        .then(confirm => {
          if (confirm) {
            this.removeCalculation(calculation);
          }
        });
    },
    toggleDownloadDialog(calculation) {
      this.downloadDialogState = true;
      this.selectedCalculation = calculation;
    },
    showHideCalculation(calculation) {
      const me = this;
      //Check if road netowrk is visible. Is so remove all features from map.
      const roadNetworkData = calculation.additionalData;
      for (let type in roadNetworkData) {
        // type can be 'Deafult' or 'Input'
        const state = roadNetworkData[type].state;
        if (state === true) {
          roadNetworkData[type].state = false;
          const roadNetworkSource = this.isochroneRoadNetworkLayer.getSource();
          const features = roadNetworkData[type].features;
          features.forEach(feature => {
            roadNetworkSource.removeFeature(feature);
          });
        }
      }
      me.toggleIsochroneCalculationVisibility(calculation);
    },
    showPoisTable(calculation) {
      const me = this;
      const features = IsochroneUtils.getCalculationFeatures(
        calculation,
        me.isochroneLayer
      );
      const pois = IsochroneUtils.getCalculationPoisObject(features);
      const payload = {
        calculationId: calculation.id,
        calculationName: `Calculation - ${calculation.id}`,
        calculationType: calculation.calculationType,
        pois: pois
      };
      if (calculation.calculationType === "multiple") {
        const multiIsochroneTableData = IsochroneUtils.getMultiIsochroneTableData(
          features
        );
        payload.multiIsochroneTableData = multiIsochroneTableData;
      }
      me.setSelectedThematicData(payload);
      me.toggleThematicDataVisibility(true);
    },
    showAdditionalLayerDialog(calculation) {
      this.additionalLayersDialogState = true;
      this.selectedCalculation = calculation;
    }
  },
  computed: {
    ...mapGetters("isochrones", {
      calculations: "calculations",
      isochroneLayer: "isochroneLayer",
      isochroneRoadNetworkLayer: "isochroneRoadNetworkLayer"
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
}
.result-icons:hover {
  cursor: pointer;
  color: #30c2ff;
}
.isochrone-nr {
  position: absolute;
  left: 6px;
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
</style>
