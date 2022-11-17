<template>
  <v-card
    v-if="isochroneResultWindow === true"
    v-draggable="draggableValue"
    class="thematic-data isochrone-result"
    id="isochroneWindowId"
    ondragstart="return false;"
  >
    <v-layout justify-space-between column>
      <v-app-bar
        :ref="handleId"
        :color="appColor.primary"
        height="50"
        class="elevation-0"
        style="cursor:grab;"
        dark
      >
        <v-app-bar-nav-icon
          ><v-icon>fas fa-bullseye</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>Isochrone</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-icon @click="expand" class="toolbar-icons mr-2">
          {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}</v-icon
        >
        <v-icon @click="close" class="toolbar-icons ml-2">fas fa-times</v-icon>
      </v-app-bar>

      <vue-scroll>
        <div>
          <v-flex v-if="isExpanded" xs12 class="mx-3 mt-1 mb-1">
            <v-card-text class="ma-0 pa-0" row>
              <v-row justify="center" align="center" class="mx-1">
                <v-menu offset-y>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      fab
                      icon
                      class="elevation-0"
                      v-on="on"
                      v-bind="attrs"
                      small
                    >
                      <v-icon small>fa-solid fa-download</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item
                      v-for="(type, index) in isochroneDownloadTypes"
                      @click="downloadIsochrone(type)"
                      :key="index"
                    >
                      <v-list-item-title>{{ type }}</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
                <v-spacer></v-spacer>
                <template
                  v-if="
                    selectedCalculations.length > 1 &&
                      ![0, 2].includes(resultViewType)
                  "
                >
                  <div
                    class="mx-2 colorPalettePicker"
                    :style="
                      `border-bottom:4px solid ${
                        preDefCalculationColors[selectedCalculations[0].id - 1]
                      };`
                    "
                  ></div>
                  <span
                    >Isochrone
                    {{
                      getCurrentIsochroneNumber(selectedCalculations[0])
                    }}</span
                  >
                  <div
                    class="ml-6 mr-2 colorPalettePicker"
                    :style="
                      `border-bottom:4px dashed ${
                        preDefCalculationColors[selectedCalculations[1].id - 1]
                      };`
                    "
                  ></div>
                  <span
                    >Isochrone
                    {{
                      getCurrentIsochroneNumber(selectedCalculations[1])
                    }}</span
                  >
                </template>
                <v-spacer></v-spacer>
                <v-btn-toggle
                  v-model="resultViewType"
                  v-if="selectedCalculations[0].type !== 'multiple'"
                  mandatory
                >
                  <v-btn small>
                    <v-icon small>fa-solid fa-table</v-icon>
                  </v-btn>
                  <v-btn small>
                    <v-icon small>fa-solid fa-chart-line</v-icon>
                  </v-btn>
                  <v-btn
                    small
                    :disabled="
                      (selectedPoisOnlyKeys.length < 2 &&
                        selectedAoisOnlyKeys.length < 2 &&
                        selectedCalculations.length === 1) ||
                        (selectedPoisOnlyKeys.length < 3 &&
                          selectedAoisOnlyKeys.length < 3 &&
                          selectedCalculations.length === 2)
                    "
                  >
                    <v-icon small>fa-solid fa-chart-pie</v-icon>
                  </v-btn>
                </v-btn-toggle>
              </v-row>
            </v-card-text>
            <isochrone-amenities-line-chart
              :width="550"
              :height="300"
              v-if="selectedCalculations && resultViewType === 1"
            />

            <isochrone-amenities-pie-chart
              :calculationIndex="0"
              :height="300"
              v-if="
                selectedCalculations &&
                  selectedCalculations.length === 1 &&
                  resultViewType === 2 &&
                  (selectedPoisOnlyKeys.length > 1 ||
                    selectedAoisOnlyKeys.length > 1)
              "
            />
            <isochrone-amenities-radar-chart-vue
              :height="300"
              v-if="
                selectedCalculations &&
                  selectedCalculations.length === 2 &&
                  resultViewType === 2 &&
                  (selectedPoisOnlyKeys.length > 2 ||
                    selectedAoisOnlyKeys.length > 2)
              "
            ></isochrone-amenities-radar-chart-vue>
            <v-btn-toggle
              v-if="resultViewType !== 0"
              v-model="chartDatasetType"
              mandatory
            >
              <v-btn :disabled="resultViewType !== 1" small>
                <i
                  class="v-icon notranslate fa-solid fa-people-group theme--light"
                  style="font-size: 16px;"
                ></i>
              </v-btn>
              <v-btn small :disabled="selectedPoisOnlyKeys.length < 1">
                <v-icon small>fa-solid fa-location-dot</v-icon>
              </v-btn>
              <v-btn small :disabled="selectedAoisOnlyKeys.length < 1">
                <i
                  class="v-icon notranslate fa-brands fa-square-pied-piper theme--light"
                  style="font-size: 16px;"
                ></i>
              </v-btn>
            </v-btn-toggle>
            <v-data-table
              v-if="resultViewType === 0"
              :headers="tableHeaders"
              :items="tableItems"
              class="mb-2"
              style="max-height: 250px;"
              :search="search"
              hide-default-footer
              :no-data-text="
                selectedTime === null
                  ? $t('isochrones.tableData.selectTimeMsg')
                  : $t('isochrones.tableData.noDataMsg')
              "
              :items-per-page="-1"
            >
              <template v-slot:items="props">
                <td v-for="(header, index) in tableHeaders" :key="index">
                  {{ props.item[header.value] }}
                </td>
              </template>
            </v-data-table>
          </v-flex>
        </div>
      </vue-scroll>
    </v-layout>
  </v-card>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import IsochroneUtils from "../../utils/IsochroneUtils";
import { Draggable } from "draggable-vue-directive";
import { mapFields } from "vuex-map-fields";
import { featuresToGeojson } from "../../utils/MapUtils";
import IsochroneAmenitiesLineChart from "../other/IsochroneAmenitiesLineChart.vue";
import IsochroneAmenitiesPieChart from "../other/IsochroneAmenitiesPieChart.vue";
import IsochroneAmenitiesRadarChartVue from "../other/IsochroneAmenitiesRadarChart.vue";
import { saveAs } from "file-saver";
import { debounce, numberSeparator } from "../../utils/Helpers";
import ApiService from "../../services/api.service";
import JSZip from "jszip";
import {
  calculateCalculationsLength,
  calculateCurrentIndex
} from "../../utils/Helpers";
export default {
  components: {
    IsochroneAmenitiesLineChart,
    IsochroneAmenitiesPieChart,
    IsochroneAmenitiesRadarChartVue
  },
  directives: {
    Draggable
  },
  data: () => ({
    isochroneSteps: [],
    selectedTime: null,
    search: "",
    resultViewType: 0,
    isExpanded: true,
    //Vue windows\ draggable
    handleId: "handle-id",
    draggableValue: {
      handle: undefined,
      boundingElement: undefined,
      resetInitialPos: undefined
    },
    downloadDialogState: false,
    selectedCalculationForDownload: null,
    isochroneDownloadTypes: ["GeoJSON", "ESRI Shapefile", "XLSX"]
  }),
  methods: {
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    }),
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    close() {
      this.isochroneLayer
        .getSource()
        .getFeatures()
        .forEach(f => {
          f.set("highlightFeature", false);
        });
      this.isochroneResultWindow = false;
    },
    stopPropagation(e) {
      e.stopPropagation();
    },
    getString(val) {
      let string = "";
      if (typeof val === "object" && val.cnt && val.area) {
        const value = `${val.cnt} (${val.area} m2)`;
        string = value;
      } else {
        string = val;
      }
      return string;
    },
    updateIsochroneSurface: debounce(function() {
      this.selectedCalculations.forEach(calculation => {
        IsochroneUtils.updateIsochroneSurface(
          calculation,
          this.calculationTravelTime[calculation.id - 1]
        );
      });
    }, 30),
    downloadIsochrone(type) {
      const promiseArray = [];
      this.selectedCalculations.forEach(calculation => {
        const feature = calculation.feature.clone();
        const reached_opportunities = {};
        const accessibility = calculation.surfaceData.accessibility;
        if (calculation.type === "single") {
          Object.keys(accessibility).forEach(category => {
            reached_opportunities[category] =
              accessibility[category][this.isochroneRange - 1];
          });
        } else {
          Object.keys(accessibility).forEach(studyAreaId => {
            reached_opportunities[studyAreaId] = {
              reached_population:
                accessibility[studyAreaId]["reached_population"][
                  this.isochroneRange - 1
                ],
              total_population: accessibility[studyAreaId]["total_population"]
            };
          });
        }
        const properties = {
          isochrone_calculation_id: calculation.id,
          traveltime: this.isochroneRange,
          modus: calculation.config.scenario.modus,
          routing_profile: calculation.routing,
          reached_opportunities
        };
        feature.setProperties(properties);
        const geojsonPayload = featuresToGeojson(
          [feature],
          "EPSG:3857",
          "EPSG:4326"
        );
        promiseArray.push(
          ApiService.post(
            `/isochrones/export?return_type=${type}`,
            geojsonPayload,
            {
              responseType: "blob",
              headers: {
                "Content-Type": "application/json"
              }
            }
          )
        );
      });
      Promise.all(promiseArray)
        .then(responses => {
          const zip = new JSZip();
          responses.forEach((response, index) => {
            const exportName = `isochrone-export_${index}_${this.isochroneRange}-min.zip`;
            if (responses.length === 1) {
              saveAs(response.data, exportName);
            }
            zip.file(exportName, response.data, { blob: true });
          });
          if (responses.length > 1) {
            zip.generateAsync({ type: "blob" }).then(function(content) {
              saveAs(content, "isochrone-export.zip");
            });
          }
        })
        .catch(e => {
          console.log(e);
          this.toggleSnackbar({
            type: "error",
            message: "Error downloading isochrones",
            state: true,
            timeout: 10000
          });
        });
    },
    getCurrentIsochroneNumber(calc) {
      return calculateCalculationsLength() - calculateCurrentIndex(calc);
    }
  },
  computed: {
    tableHeaders() {
      let headers;
      // Single Isochrone calculation table header
      if (
        this.selectedCalculations.length > 0 &&
        this.selectedCalculations[0].type === "single"
      ) {
        headers = [
          {
            text: this.$t("isochrones.tableData.table.pois"),
            value: "pois",
            sortable: false
          }
        ];
        this.selectedCalculations.forEach(calculation => {
          const id = this.getCurrentIsochroneNumber(calculation);
          // const modus = calculation.config.scenario.modus;
          headers.push({
            text: `Isochrone #${id}`,
            value: `isochrone-${id}`,
            sortable: false
          });
        });
      } else {
        headers = [
          {
            text: this.$t("isochrones.tableData.table.studyArea"),
            value: "studyArea",
            sortable: false,
            width: "25%"
          },
          {
            text: this.$t("isochrones.tableData.table.population"),
            value: "population",
            sortable: false,
            width: "25%"
          },
          {
            text: this.$t("isochrones.tableData.table.reachedPopulation"),
            value: "reachPopulation",
            sortable: false,
            width: "25%"
          },
          {
            text: this.$t("isochrones.tableData.table.shared"),
            value: "shared",
            sortable: false,
            width: "20%"
          }
        ];
      }
      return headers;
    },
    tableItems() {
      let items = [];
      let poisObj = {};
      this.selectedCalculations.forEach(calculation => {
        // Single isochrone calculation
        let pois = calculation.surfaceData.accessibility;
        let selectedTime = this.calculationTravelTime[calculation.id - 1];
        if (calculation.type === "single") {
          let keys = Object.keys(pois);
          if (keys.length > 0) {
            let sumPois = {};
            keys.forEach(poiKey => {
              sumPois[poiKey] = pois[poiKey][selectedTime - 1];
            });
            if (sumPois) {
              //Loop through  amenities
              keys.forEach(amenity => {
                let isAmenitySelected = this.poisAois[amenity];
                if (amenity === "population") {
                  isAmenitySelected = true;
                }
                if (isAmenitySelected) {
                  let obj = {
                    pois: amenity ? this.$t(`pois.${amenity}`) : amenity
                  };
                  let value = numberSeparator(
                    this.getString(parseInt(sumPois[amenity])),
                    this.$i18n.locale
                  );
                  obj[`isochrone-${calculation.id}`] = value || "-";
                  if (poisObj[amenity]) {
                    poisObj[amenity] = { ...poisObj[amenity], ...obj };
                  } else {
                    poisObj[amenity] = obj;
                  }
                }
              });
            }
          }
        } else {
          Object.keys(pois).forEach(studyArea => {
            const reachedPopulation =
              pois[studyArea].reached_population[selectedTime - 1];
            items.push({
              studyArea: studyArea,
              population: parseInt(pois[studyArea].total_population),
              reachPopulation: parseInt(reachedPopulation),
              shared: `${(
                (reachedPopulation / pois[studyArea].total_population) *
                100
              ).toFixed(1)}%`
            });
          });
        }
      });
      //Sort table rows based on number of amenties || alphabeticaly (only on single calculations)
      if (this.calculations[0].type === "single") {
        items = Object.values(poisObj);
        items.sort((a, b) => {
          const b_Value = b[Object.keys(b)[0]];
          const a_Value = a[Object.keys(a)[0]];
          if (b_Value === a_Value) {
            return a["pois"].localeCompare(b["pois"]);
          }
          return b_Value - a_Value;
        });
      }
      return items;
    },
    getMaxIsochroneRange() {
      let maxIsochroneRange = 60;
      const walkingCyclingCalculations = this.selectedCalculations.filter(
        c => !["transit", "car"].includes(c.routing)
      );
      if (walkingCyclingCalculations.length > 0) {
        maxIsochroneRange = 20;
      }
      return maxIsochroneRange;
    },
    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer",
      calculationColors: "calculationColors",
      preDefCalculationColors: "preDefCalculationColors",
      calculationSrokeObjects: "calculationSrokeObjects",
      calculationTravelTime: "calculationTravelTime",
      selectedCalculationChangeColor: "selectedCalculationChangeColor"
    }),
    ...mapGetters("poisaois", {
      poisAois: "poisAois",
      selectedPois: "selectedPois",
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys",
      selectedAoisOnlyKeys: "selectedAoisOnlyKeys"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    ...mapFields("isochrones", {
      calculations: "calculations",
      selectedCalculations: "selectedCalculations",
      chartDatasetType: "chartDatasetType",
      isochroneRange: "isochroneRange",
      isochroneResultWindow: "isochroneResultWindow"
    })
  },
  watch: {
    calculationColors() {
      this.updateIsochroneSurface(this.selectedCalculationChangeColor);
    },
    calculationSrokeObjects() {
      this.updateIsochroneSurface(this.selectedCalculationChangeColor);
    },
    resultViewType(value) {
      if (value === 2 && this.chartDatasetType === 0) {
        if (this.selectedPoisOnlyKeys.length > 0) {
          this.chartDatasetType = 1;
        } else {
          this.chartDatasetType = 2;
        }
      }
    },
    selectedPoisOnlyKeys(value) {
      if (this.chartDatasetType === 1 && value.length < 2) {
        if (this.selectedAoisOnlyKeys.length >= 1) {
          this.chartDatasetType = 2;
        } else {
          this.chartDatasetType = 0;
          this.resultViewType = 1;
        }
      }
      if (
        value.length < 2 &&
        this.resultViewType === 2 &&
        this.selectedCalculations.length === 1 &&
        this.chartDatasetType === 1
      ) {
        this.resultViewType = 1;
      }
      if (
        this.selectedCalculations.length === 2 &&
        value.length < 3 &&
        this.resultViewType === 2 &&
        this.chartDatasetType === 1
      ) {
        this.chartDatasetType = 0;
        this.resultViewType = 1;
      }
    },
    selectedAoisOnlyKeys(value) {
      if (this.chartDatasetType === 2 && value.length < 2) {
        if (this.selectedPoisOnlyKeys.length >= 1) {
          this.chartDatasetType = 1;
        } else {
          this.chartDatasetType = 0;
          this.resultViewType = 1;
        }
      }
      if (
        value.length < 2 &&
        this.resultViewType === 2 &&
        this.selectedCalculations.length === 1 &&
        this.chartDatasetType === 2
      ) {
        this.resultViewType = 1;
      }
      if (
        this.selectedCalculations.length === 2 &&
        value.length < 3 &&
        this.resultViewType === 2 &&
        this.chartDatasetType === 2
      ) {
        this.chartDatasetType = 0;
        this.resultViewType = 1;
      }
    },
    selectedCalculations(newSelection, oldSelection) {
      if (
        newSelection.length > 0 &&
        newSelection.length >= oldSelection.length
      ) {
        // Update new calculation
        this.updateIsochroneSurface(newSelection[newSelection.length - 1]);
      }
    }
  },
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
  }
};
</script>
<style scoped>
.toolbar-icons:hover {
  cursor: pointer;
}
.thematic-data {
  transition: height 0.1s linear;
}
.colorPalettePicker {
  width: 50px;
  border-radius: 0px;
  margin-bottom: 16px;
}

.isochrone-result {
  position: fixed;
  z-index: 2;
  top: 20px;
  /** Drawer width + 70px margin */
  left: calc(360px + 70px);
  max-width: 600px;
  min-width: 370px;
  height: fit-content;
}
</style>
