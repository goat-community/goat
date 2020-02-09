<template>
  <v-card
    v-if="selectedThematicData"
    v-show="isThematicDataVisible"
    v-draggable="draggableValue"
    class="elevation-4"
    id="isochroneWindowId"
    :style="[isExpanded ? { height: '450px' } : { height: '60px' }]"
    style="position:fixed;top:10px;left:360px;z-index:2;max-width:350px;min-width:350px;height:450px;overflow:hidden;"
  >
    <v-expand-transition>
      <v-layout justify-space-between column fill-height>
        <v-app-bar :ref="handleId" color="green" style="cursor:grab;" dark>
          <v-app-bar-nav-icon
            ><v-icon>fas fa-bullseye</v-icon></v-app-bar-nav-icon
          >
          <v-toolbar-title>Isochrone</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-icon @click="expand" class="toolbar-icons mr-2">
            {{
              isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down"
            }}</v-icon
          >
          <v-icon @click="close" class="toolbar-icons ml-2"
            >fas fa-times</v-icon
          >
        </v-app-bar>

        <vue-scroll>
          <v-flex v-if="isExpanded" xs12 class="mx-3 mt-1">
            <v-card-text class="ma-0 py-0 pt-0 pb-2">
              <v-layout row wrap justify-end>
                <v-flex shrink>
                  <v-chip class="mt-1 mb-0">
                    {{
                      `${$t("isochrones.calculation")} - ${
                        selectedThematicData.calculationId
                      }`
                    }}
                  </v-chip></v-flex
                ></v-layout
              >
            </v-card-text>
            <v-select
              v-if="selectedThematicData.calculationType === 'single'"
              :items="isochroneSteps"
              item-text="display"
              item-value="value"
              :label="$t('isochrones.tableData.timeFilter')"
              v-model="selectedTime"
            ></v-select>

            <v-text-field
              v-if="selectedThematicData.calculationType === 'single'"
              v-model="search"
              append-icon="search"
              :label="$t('isochrones.tableData.searchPois')"
              single-line
              hide-details
              class="mb-2 pt-0 mt-0"
            ></v-text-field>

            <v-data-table
              :headers="tableHeaders"
              :items="tableItems"
              class="elevation-1 mb-2"
              :search="search"
              :no-data-text="
                selectedTime === null
                  ? $t('isochrones.tableData.selectTimeMsg')
                  : $t('isochrones.tableData.noDataMsg')
              "
              :items-per-page-options="[
                5,
                10,
                15,
                { text: '$vuetify.dataIterator.rowsPerPageAll', value: -1 }
              ]"
              :options.sync="pagination"
            >
              <template v-slot:items="props">
                <td v-for="(header, index) in tableHeaders" :key="index">
                  {{ props.item[header.value] }}
                </td>
              </template>
            </v-data-table>

            <v-alert
              v-if="
                getPoisItems.length === 0 &&
                  selectedThematicData.calculationType === 'single'
              "
              border="left"
              colored-border
              class="mb-1 mt-2 elevation-2"
              icon="info"
              color="green"
              dense
            >
              <span
                v-html="$t('isochrones.tableData.selectAmenitiesMsg')"
              ></span>
            </v-alert>
          </v-flex>
        </vue-scroll>
      </v-layout>
    </v-expand-transition>
  </v-card>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import IsochroneUtils from "../../../utils/IsochroneUtils";
import { Draggable } from "draggable-vue-directive";

export default {
  directives: {
    Draggable
  },
  data: () => ({
    pagination: {
      rowsPerPage: 10
    },
    selectedTime: null,
    search: "",
    isExpanded: true,
    //Vue windows\ draggable
    handleId: "handle-id",
    draggableValue: {
      handle: undefined,
      boundingElement: undefined,
      resetInitialPos: undefined
    }
  }),
  methods: {
    isAmenitySelected(amenity) {
      let isChecked;
      this.selectedThematicData.filterSelectedPois.forEach(item => {
        if (item["weight"] && !item["children"] && item.value === amenity) {
          isChecked = true;
        }
      });
      return isChecked;
    },
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
      this.toggleThematicDataVisibility(false);
    },
    ...mapMutations("isochrones", {
      toggleThematicDataVisibility: "TOGGLE_THEMATIC_DATA_VISIBILITY"
    })
  },
  computed: {
    tableHeaders() {
      let headers;
      if (this.selectedThematicData.calculationType === "single") {
        let pois = this.selectedThematicData.pois;
        headers = [
          {
            text: this.$t("isochrones.tableData.table.pois"),
            value: "pois",
            sortable: false
          }
        ];

        const keys = Object.keys(pois);

        for (const key of keys) {
          headers.push({
            text: IsochroneUtils.getIsochroneAliasFromKey(key),
            value: key,
            sortable: false
          });
        }
      } else {
        headers = [
          {
            text: this.$t("isochrones.tableData.table.isochrone"),
            value: "isochrone",
            sortable: false,
            width: "32%"
          },
          {
            text: this.$t("isochrones.tableData.table.studyArea"),
            value: "studyArea",
            sortable: false,
            width: "18%"
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
          }
        ];
      }
      return headers;
    },
    isochroneSteps() {
      let pois = this.selectedThematicData.pois;
      let timeValues = [];
      if (pois) {
        for (const key in pois) {
          let obj = pois[key];
          for (const prop in obj) {
            timeValues.push({ display: `${prop} min`, value: `${prop}` });
          }
          break;
        }
      }
      return timeValues;
    },
    tableItems() {
      let me = this;
      let items = [];
      if (me.selectedThematicData.calculationType === "single") {
        let pois = me.selectedThematicData.pois;
        let selectedTime = me.selectedTime;
        let keys = Object.keys(pois);
        if (keys.length > 0) {
          let sumPois = pois[keys[0]][selectedTime];
          if (sumPois) {
            //Loop through  amenities
            for (const amenity in sumPois) {
              let isAmenitySelected = me.isAmenitySelected(amenity);
              if (amenity === "population") {
                isAmenitySelected = true;
              }
              if (isAmenitySelected) {
                let obj = {
                  pois: amenity ? this.$t(`pois.${amenity}`) : amenity
                };
                //Default or input calculation
                obj[keys[0]] = sumPois[amenity];
                //Double calculation
                if (pois[keys[1]]) {
                  obj[keys[1]] = pois[keys[1]][selectedTime][amenity];
                }
                items.push(obj);
              }
            }
          }
        }
      } else {
        if (me.selectedThematicData.multiIsochroneTableData) {
          items = me.selectedThematicData.multiIsochroneTableData;
        }
      }
      return items;
    },

    ...mapGetters("isochrones", {
      selectedThematicData: "selectedThematicData",
      isThematicDataVisible: "isThematicDataVisible",
      isochroneLayer: "isochroneLayer"
    }),

    ...mapGetters("pois", {
      getPoisItems: "selectedPois"
    })
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
</style>
