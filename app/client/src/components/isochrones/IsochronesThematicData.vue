<template>
  <v-layout>
    <v-flex xs12 class="mx-3">
      <v-card-text class="ma-0 py-0 pt-0 pb-2">
        <p class="font-weight-medium  text-right ma-0 pa-0">
          - {{ selectedThematicData.calculationName }}
        </p>
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
        <span v-html="$t('isochrones.tableData.selectAmenitiesMsg')"></span>
      </v-alert>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";
import IsochroneUtils from "../../utils/IsochroneUtils";
export default {
  data: () => ({
    pagination: {
      rowsPerPage: 10
    },
    selectedTime: null,
    search: ""
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
    }
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
      selectedThematicData: "selectedThematicData"
    }),
    ...mapGetters("pois", {
      getPoisItems: "selectedPois"
    })
  }
};
</script>
