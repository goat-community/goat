<template>
  <v-dialog v-model="show" max-width="500px">
    <v-card class="">
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-chart-line</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title
          >Heatmap - ({{ selectedAmenity.name }})</v-toolbar-title
        >

        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <v-card-text>
        <v-select
          v-model="selectedAmenity.weight"
          :items="weightListValues"
          class="mx-2"
          label="Select Weight"
          outlined
        ></v-select>
        <v-checkbox
          class="ml-2"
          v-model="expertHeatmap"
          label="Expert Heatmap"
        ></v-checkbox>
        <template v-if="expertHeatmap === true">
          <v-combobox
            v-model="selectedAmenity.sensitivity"
            :items="sensitivityListValues"
            class="mx-2"
            label="Sensitivity index"
            outlined
          ></v-combobox>
          <sensitivity-chart :amenity="selectedAmenity" />
        </template>
      </v-card-text>
      <v-card-actions> </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import SensitivityChart from "../../other/chart/SensitivityChart";

export default {
  components: {
    SensitivityChart
  },
  data() {
    return {
      expertHeatmap: false,
      weightListValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      sensitivityListValues: [-0.001, -0.002, -0.003]
    };
  },
  props: {
    visible: { type: Boolean, required: false, default: false },
    selectedAmenity: { type: Object }
  },
  computed: {
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    }
  }
};
</script>
