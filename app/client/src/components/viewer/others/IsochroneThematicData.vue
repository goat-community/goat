<template>
  <v-card
    v-if="selectedThematicData"
    v-show="isThematicDataVisible"
    v-draggable="draggableValue"
    class="thematic-data elevation-4"
    id="isochroneWindowId"
    :style="[isExpanded ? { height: '400px' } : { height: '50px' }]"
    style="position:fixed;top:10px;left:360px;z-index:2;max-width:370px;min-width:370px;height:450px;overflow:hidden;"
  >
    <v-layout justify-space-between column fill-height>
      <v-app-bar
        :ref="handleId"
        color="green"
        height="50"
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
        <v-flex v-if="isExpanded" xs12 class="mx-3 mt-1">
          <v-card-text class="ma-0 py-0 pt-0 pb-2">
            <v-layout row wrap justify-end>
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

          <v-data-table
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
      </vue-scroll>
    </v-layout>
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
    isochroneSteps: [],
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
    tableItems() {
      let me = this;
      let items = [];
      if (me.selectedThematicData.calculationType === "single") {
        let pois = me.selectedThematicData.pois;
        let selectedTime = me.selectedTime;
        let keys = Object.keys(pois);
        if (keys.length > 0) {
          let sumPois = pois[keys[0]][selectedTime];
          let amenityNames = Object.keys(pois[keys[0]][selectedTime]);
          // Only if double-calculation
          if (keys.length === 2) {
            const inputAmenityNames = Object.keys(pois[keys[1]][selectedTime]);
            if (Array.isArray(inputAmenityNames)) {
              amenityNames = [
                ...new Set([...amenityNames, ...inputAmenityNames])
              ];
            }
          }
          if (sumPois) {
            //Loop through  amenities
            amenityNames.forEach(amenity => {
              let isAmenitySelected = me.isAmenitySelected(amenity);
              if (amenity === "population") {
                isAmenitySelected = true;
              }
              if (isAmenitySelected) {
                let obj = {
                  pois: amenity ? this.$t(`pois.${amenity}`) : amenity
                };
                //Default or input calculation
                obj[keys[0]] = sumPois[amenity] || "-";
                //Double calculation
                if (pois[keys[1]]) {
                  obj[keys[1]] = pois[keys[1]][selectedTime][amenity] || "-";
                }
                items.push(obj);
              }
            });
          }
        }
      } else {
        if (me.selectedThematicData.multiIsochroneTableData) {
          items = me.selectedThematicData.multiIsochroneTableData;
        }
      }

      //Sort table rows based on number of amenties || alphabeticaly (only on single calculations)
      if (this.selectedThematicData.calculationType === "single") {
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
      selectedThematicData: "selectedThematicData",
      isThematicDataVisible: "isThematicDataVisible",
      isochroneLayer: "isochroneLayer"
    }),

    ...mapGetters("pois", {
      getPoisItems: "selectedPois"
    })
  },
  watch: {
    selectedThematicData(value) {
      this.isochroneSteps = [];
      if (!value) return;
      let pois = value.pois;
      if (pois) {
        for (const key in pois) {
          let obj = pois[key];
          for (const prop in obj) {
            this.isochroneSteps.push({
              display: `${prop} min`,
              value: `${prop}`
            });
          }
          break;
        }
        this.selectedTime =
          this.isochroneSteps.length > 0
            ? this.isochroneSteps[this.isochroneSteps.length - 1].value
            : [];
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
</style>
