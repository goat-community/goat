<template>
  <v-dialog v-model="show" scrollable max-width="500px">
    <v-card class="">
      <v-app-bar :color="color" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-chart-line</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title
          >{{ $t("appBar.filter.poisSettings.title") }} - ({{
            getDisplayName(selectedAmenity)
          }})</v-toolbar-title
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
            :label="$t('appBar.filter.poisSettings.selectWeight')"
            outlined
          ></v-select>
          <template>
            <v-select
              v-model="selectedAmenity.sensitivity"
              :items="sensitivityListValues"
              @change="updateHeatmap"
              class="mx-2"
              :label="$t('appBar.filter.poisSettings.sensitivityIndex')"
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
import { EventBus } from "../../../EventBus";
import SensitivityChart from "../../other/SensitivityChart";

export default {
  components: {
    SensitivityChart
  },
  data() {
    return {
      weightListValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      sensitivityListValues: [
        150000,
        200000,
        250000,
        300000,
        350000,
        400000,
        450000
      ]
    };
  },

  props: {
    visible: { type: Boolean, required: false, default: false },
    selectedAmenity: { type: Object },
    color: { type: String, default: "#2BB381" }
  },
  methods: {
    updateHeatmap() {
      EventBus.$emit("update-heatmap", "poi");
    },
    getDisplayName(item) {
      let value;
      if (item.value) {
        //Display name for amenities
        value = this.$t(`pois.${item.value}`);
      }
      return value;
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
