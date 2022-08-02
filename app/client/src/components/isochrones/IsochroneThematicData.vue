<template>
  <v-card
    v-if="selectedCalculations.length > 0"
    v-draggable="draggableValue"
    class="thematic-data elevation-4"
    id="isochroneWindowId"
    :style="[isExpanded ? { height: '520px' } : { height: '50px' }]"
    style="position:fixed;top:10px;left:400px;z-index:2;max-width:600px;min-width:370px;height:450px;overflow:hidden;"
    ondragstart="return false;"
  >
    <v-layout justify-space-between column fill-height>
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
          <v-flex v-if="isExpanded" xs12 class="mx-3 mt-1">
            <v-card-text class="ma-0 py-0 pt-0 pb-2">
              <v-layout row wrap justify-end> </v-layout>
            </v-card-text>
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
                    :style="`border-bottom:4px solid ${calculationColors[0]};`"
                  ></div>
                  <span>Isochrone {{ selectedCalculations[0].id }}</span>
                  <div
                    class="ml-6 mr-2 colorPalettePicker"
                    :style="`border-bottom:4px dashed ${calculationColors[1]};`"
                  ></div>
                  <span>Isochrone {{ selectedCalculations[1].id }}</span>
                </template>
                <v-spacer></v-spacer>
                <v-btn-toggle v-model="resultViewType" mandatory>
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
                        selectedCalculations.length === 1) ||
                        (selectedPoisOnlyKeys.length < 3 &&
                          selectedCalculations.length === 2)
                    "
                  >
                    <v-icon small>fa-solid fa-chart-pie</v-icon>
                  </v-btn>
                </v-btn-toggle>
              </v-row>
              <v-row class="ml-1 mr-0">
                <v-col cols="12" class="pr-0 pb-0 mr-0">
                  <v-slider
                    @mousedown.native.stop
                    @mouseup.native.stop
                    @click.native.stop
                    class="pt-4"
                    prepend-icon="schedule"
                    :track-color="appColor.secondary"
                    :color="appColor.secondary"
                    v-model="isochroneRange"
                    :min="1"
                    :max="60"
                    thumb-label="always"
                    thumb-size="25"
                    @input="udpateIsochroneSurface"
                  >
                    <template v-slot:thumb-label="{ value }">
                      {{ value }}
                    </template>
                  </v-slider>
                </v-col>
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
                  selectedPoisOnlyKeys.length > 1
              "
            />
            <isochrone-amenities-radar-chart-vue
              :height="300"
              v-if="
                selectedCalculations &&
                  selectedCalculations.length === 2 &&
                  resultViewType === 2 &&
                  selectedPoisOnlyKeys.length > 2
              "
            ></isochrone-amenities-radar-chart-vue>
            <v-btn-toggle
              v-if="
                [1].includes(resultViewType) && selectedPoisOnlyKeys.length > 0
              "
              v-model="chartDatasetType"
              mandatory
            >
              <v-btn small>
                <i
                  class="v-icon notranslate fa-solid fa-people-group theme--light"
                  style="font-size: 16px;"
                ></i>
              </v-btn>
              <v-btn small>
                <v-icon small>fa-solid fa-location-dot</v-icon>
              </v-btn>
            </v-btn-toggle>
            <v-data-table
              v-if="resultViewType === 0"
              :headers="tableHeaders"
              :items="tableItems"
              class="elevation-1 mb-2"
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
import { mapGetters } from "vuex";
// import IsochroneUtils from "../../utils/IsochroneUtils";
import { Draggable } from "draggable-vue-directive";
import { mapFields } from "vuex-map-fields";
import { fromPixel, geojsonToFeature } from "../../utils/MapUtils";
import { jsolines } from "../../utils/Jsolines";
import IsochroneAmenitiesLineChart from "../other/IsochroneAmenitiesLineChart.vue";
import IsochroneAmenitiesPieChart from "../other/IsochroneAmenitiesPieChart.vue";
import IsochroneAmenitiesRadarChartVue from "../other/IsochroneAmenitiesRadarChart.vue";
import { debounce } from "../../utils/Helpers";
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
    isochroneDownloadTypes: ["GeoJson", "Shapefile", "XLSX"]
  }),
  methods: {
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
      this.selectedCalculations = [];
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
    udpateIsochroneSurface: debounce(function(cutoff) {
      this.selectedCalculations.forEach(calculation => {
        const {
          surface,
          width,
          height,
          west,
          north,
          zoom
          // eslint-disable-next-line no-undef
        } = calculation.surfaceData;
        const isochronePolygon = jsolines({
          surface,
          width,
          height,
          cutoff: cutoff,
          project: ([x, y]) => {
            const ll = fromPixel({ x: x + west, y: y + north }, zoom);
            return [ll.lon, ll.lat];
          }
        });
        let olFeatures = geojsonToFeature(isochronePolygon, {
          dataProjection: "EPSG:4326",
          featureProjection: "EPSG:3857"
        });
        calculation.feature.setGeometry(olFeatures[0].getGeometry());
      });
    }, 30),
    downloadIsochrone(type) {
      console.log(type);
    }
  },
  computed: {
    tableHeaders() {
      let headers;
      // Single Isochrone calculation table header
      if (
        this.selectedCalculations.length > 0 &&
        this.selectedCalculations[0].config.starting_point.input.length === 1
      ) {
        headers = [
          {
            text: this.$t("isochrones.tableData.table.pois"),
            value: "pois",
            sortable: false
          }
        ];
        this.selectedCalculations.forEach(calculation => {
          const id = calculation.id;
          // const modus = calculation.config.scenario.modus;
          headers.push({
            text: `Isochrone - ${id}`,
            value: `isochrone-${id}`,
            sortable: false
          });
        });
      } else {
        headers = [
          {
            text: this.$t("isochrones.tableData.table.isochrone"),
            value: "isochrone",
            sortable: false,
            width: "25%"
          },
          {
            text: this.$t("isochrones.tableData.table.studyArea"),
            value: "studyArea",
            sortable: false,
            width: "15%"
          },
          {
            text: this.$t("isochrones.tableData.table.population"),
            value: "population",
            sortable: false,
            width: "20%"
          },
          {
            text: this.$t("isochrones.tableData.table.reachedPopulation"),
            value: "reachPopulation",
            sortable: false,
            width: "20%"
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
        if (calculation.config.starting_point.input.length === 1) {
          let pois = calculation.surfaceData.accessibility;
          let selectedTime = this.isochroneRange;
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
                  let value = this.getString(parseInt(sumPois[amenity]));
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
          // TODO:
          console.log("multi isochrone calculation");
        }
      });
      items = Object.values(poisObj);
      //Sort table rows based on number of amenties || alphabeticaly (only on single calculations)
      if (this.calculations[0].config.starting_point.input.length === 1) {
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

    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer",
      calculationColors: "calculationColors"
    }),
    ...mapGetters("poisaois", {
      poisAois: "poisAois",
      selectedPois: "selectedPois",
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    ...mapFields("isochrones", {
      calculations: "calculations",
      selectedCalculations: "selectedCalculations",
      chartDatasetType: "chartDatasetType",
      isochroneRange: "isochroneRange"
    })
  },
  watch: {
    selectedPoisOnlyKeys(value) {
      if (value.length > 0) {
        // Show amenities
        this.chartDatasetType = 1;
      } else {
        // Show population
        this.chartDatasetType = 0;
      }
      if (
        value.length < 3 &&
        this.resultViewType === 2 &&
        this.selectedCalculations.length === 1
      ) {
        this.resultViewType = 1;
      }
      if (
        this.selectedCalculations.length === 2 &&
        value.length < 3 &&
        this.resultViewType === 2
      ) {
        this.chartDatasetType = 0;
        this.resultViewType = 1;
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
</style>
