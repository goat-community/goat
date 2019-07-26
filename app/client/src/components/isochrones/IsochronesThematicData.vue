<template>
  <v-layout>
    <v-flex xs12 class="mx-5">
      <v-card-text class="ma-0 pa-0">
        <p class="font-weight-medium  text-right ma-0 pa-0">
          - {{ selectedThematicData.calculationName }}
        </p>
      </v-card-text>

      <v-select
        :items="isochroneSteps"
        item-text="display"
        item-value="value"
        label="Time filter"
        v-model="selectedTime"
      ></v-select>

      <v-text-field
        v-model="search"
        append-icon="search"
        label="Search Point of Interest"
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
            ? 'Select time to filter'
            : 'No data for the selected time'
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
      <span v-if="getPoisItems.length === 0" style="color: red;"
        ><i>Note: Select Amenities and Time to filter the table. </i></span
      >
    </v-flex>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";
import helpers from "../../utils/Helpers";
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
      let pois = this.selectedThematicData.pois;
      let headers = [
        {
          text: "Point of Interest",
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
      let pois = me.selectedThematicData.pois;
      let selectedTime = me.selectedTime;
      let items = [];
      let keys = Object.keys(pois);

      if (keys.length > 0) {
        let sumPois = pois[keys[0]][selectedTime];
        if (sumPois) {
          //Loop through  amenities
          for (const amenity in sumPois) {
            let isAmenitySelected = me.isAmenitySelected(amenity);
            if (isAmenitySelected) {
              let obj = {
                pois: helpers.humanize(amenity)
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
