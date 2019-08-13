<template>
  <v-dialog v-model="show" max-width="500px">
    <v-card class="">
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-chart-line</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title
          >Dynamic Heatmap - ({{ selectedAmenity.name }})</v-toolbar-title
        >

        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <v-card-text>
        <!-- <v-select class="mx-2" label="Select sensitivity" outlined></v-select> -->
        <v-text-field
          v-model="selectedAmenity.sensitivity"
          class="mx-2"
          label="Accessibility index"
          outlined
        ></v-text-field>
        <line-chart :amenity="selectedAmenity" />
      </v-card-text>
      <v-card-actions> </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import LineChart from "../../other/LineChart";

export default {
  components: {
    LineChart
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
