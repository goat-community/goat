<template>
  <v-dialog v-model="show" scrollable max-width="500px">
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
      <vue-scroll>
        <v-card-text>
          <v-select
            v-model="selectedAmenity.weight"
            :items="weightListValues"
            @change="updateHeatmap"
            class="mx-2 mt-4"
            label="Select Weight"
            outlined
          ></v-select>
          <template>
            <v-select
              v-model="selectedAmenity.sensitivity"
              :items="sensitivityListValues"
              @change="updateHeatmap"
              class="mx-2"
              label="Sensitivity index"
              outlined
            ></v-select>
            <sensitivity-chart :amenity="selectedAmenity" />
          </template>
        </v-card-text>
      </vue-scroll>
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
      weightListValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      sensitivityListValues: [
        -0.004,
        -0.0035,
        -0.003,
        -0.0025,
        -0.002,
        -0.0015,
        -0.001
      ]
    };
  },

  props: {
    visible: { type: Boolean, required: false, default: false },
    selectedAmenity: { type: Object }
  },
  methods: {
    updateHeatmap() {
      this.$emit("updated");
    }
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
