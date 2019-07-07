<template>
  <v-layout row>
    <v-flex xs12 class="mx-4">
      <v-card-text class="ma-0 pa-0">
        <p class="font-weight-medium  text-xs-right ma-0 pa-0">
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
        class="elevation-1"
        :search="search"
        :no-data-text="
          selectedTime === null
            ? 'Select time to filter'
            : 'No data for the selected time'
        "
        :rows-per-page-items="[
          5,
          10,
          15,
          { text: '$vuetify.dataIterator.rowsPerPageAll', value: -1 }
        ]"
        :pagination.sync="pagination"
      >
        <template v-slot:items="props">
          <td v-for="(header, index) in tableHeaders" :key="index">
            {{ props.item[header.value] }}
          </td>
        </template>
      </v-data-table>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";
import helpers from "../../utils/Helpers";
export default {
  data: () => ({
    pagination: {
      rowsPerPage: 15
    },
    selectedTime: null,
    search: ""
  }),
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

      //TODO: Temporary!!, Remove this from here.
      let isochroneMapping = {
        "1": "Default",
        "2": "Input"
      };
      const keys = Object.keys(pois);
      for (const key of keys) {
        headers.push({
          text: isochroneMapping[key] ? isochroneMapping[key] : key,
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
      let pois = this.selectedThematicData.pois;

      let selectedTime = this.selectedTime;
      let items = [];
      let keys = Object.keys(pois);

      if (keys.length > 0) {
        let sumPois = pois[keys[0]][selectedTime];
        if (sumPois) {
          //Loop through  pois
          for (const key in sumPois) {
            let obj = {
              pois: helpers.humanize(key)
            };
            //Default or input calculation
            obj[keys[0]] = sumPois[key];
            //Double calculation
            if (pois[keys[1]]) {
              obj[keys[1]] = pois[keys[1]][selectedTime][key];
            }
            items.push(obj);
          }
        }
      }
      return items;
    },
    ...mapGetters("isochrones", {
      selectedThematicData: "selectedThematicData"
    })
  }
};
</script>
