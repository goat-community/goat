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
                        @click="showPoisTable(calculation)"
                        small
                        v-on="on"
                        class="result-icons mr-2"
                        >fas fa-table</v-icon
                      >
                    </template>
                    <span>Show Data</span>
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
                    <span>Toggle Visibility</span>
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
                    <span>Download</span>
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
                    <span>Delete</span>
                  </v-tooltip>
                </v-layout>
              </v-layout>
              <v-card-text class="pr-0 pl-0 pt-0 pb-0">
                <v-divider></v-divider>
              </v-card-text>
            </v-card-title>
            <v-subheader
              class="clickable"
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
              <h3>{{ calculation.position }}</h3>
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
        :visible="showDialog"
        :calculation="selectedCalculation"
        @close="showDialog = false"
      ></download>
    </v-layout>
  </v-flex>
</template>
<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import Confirm from "../core/Confirm";
import Download from "./IsochronesDownload";
import IsochroneUtils from "../../utils/IsochroneUtils";

export default {
  components: {
    confirm: Confirm,
    download: Download
  },
  data() {
    return {
      headers: [
        { text: "Type", value: "type", sortable: false },
        { text: "Range", value: "range", sortable: false },
        { text: "Area", value: "area", sortable: false },
        { text: "Visible", value: "visible", sortable: false },
        { text: "Legend", value: "legend", sortable: false }
      ],
      showDialog: false,
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
          "Delete",
          "Are you sure you want to delete Calculation " +
            calculation.id +
            " ?",
          { color: "green" }
        )
        .then(confirm => {
          if (confirm) {
            this.removeCalculation(calculation);
          }
        });
    },
    toggleDownloadDialog(calculation) {
      this.showDialog = true;
      this.selectedCalculation = calculation;
    },
    showHideCalculation(calculation) {
      const me = this;
      me.toggleIsochroneCalculationVisibility(calculation);
    },
    showPoisTable(calculation) {
      const me = this;
      const features = IsochroneUtils.getCalculationFeatures(
        calculation,
        me.isochroneLayer
      );
      console.log(features);
      const pois = IsochroneUtils.getCalculationPoisObject(features);
      console.log(pois);
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
    }
  },
  computed: {
    ...mapGetters("isochrones", {
      calculations: "calculations",
      isochroneLayer: "isochroneLayer"
    })
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
</style>
