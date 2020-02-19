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
            <v-chip
              x-small
              dark
              label
              color="#676767"
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
                    <v-chip small class="mb-1 mr-1">
                      <v-avatar left>
                        <v-icon small class="text-xs-center"
                          >fas fa-clock</v-icon
                        >
                      </v-avatar>
                      {{ calculation.time }}
                    </v-chip>

                    <v-chip small class="mb-1 ">
                      <v-avatar left>
                        <v-icon small class="text-xs-center"
                          >fas fa-tachometer-alt</v-icon
                        >
                      </v-avatar>
                      {{ calculation.speed }}
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
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <div
                        class="legend"
                        @click="toggleColorPickerDialog(item)"
                        v-on="on"
                        :style="{ backgroundColor: item.color }"
                      ></div
                    ></template>
                    <span>
                      {{ $t("isochrones.results.changeColorTooltip") }}
                    </span>
                  </v-tooltip>
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
        :isochroneItem="isochroneItem"
        @close="isochroneColorPickerState = false"
      ></isochrone-color-picker>
    </v-layout>
  </v-flex>
</template>
<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import Confirm from "../core/Confirm";
import Download from "./IsochronesDownload";
import AdditionalLayers from "./IsochronesAdditionalLayers";
import IsochroneColorPicker from "./IsochroneColorPicker";

export default {
  components: {
    confirm: Confirm,
    download: Download,
    additionalLayers: AdditionalLayers,
    IsochroneColorPicker
  },
  data() {
    return {
      downloadDialogState: false,
      additionalLayersDialogState: false,
      isochroneColorPickerState: false,
      selectedCalculation: null,
      isochroneItem: null,
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
        "TOGGLE_ISOCHRONE_CALCULATION_VISIBILITY"
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
    toggleColorPickerDialog(item) {
      this.isochroneColorPickerState = true;
      this.isochroneItem = item;
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
</style>
