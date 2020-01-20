<template>
  <v-dialog v-model="show" max-width="300px" v-if="isochroneItem">
    <v-card>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon><v-icon>colorize</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{
          $t("isochrones.pickColor.title")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <v-container class="py-0">
        <v-row justify="space-around">
          <v-color-picker
            @input="updateFeatureColor"
            v-model="isochroneItem.color"
          ></v-color-picker> </v-row
      ></v-container>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: {
    isochroneItem: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  data: () => ({
    selectedIsochroneFeature: null
  }),
  methods: {
    updateFeatureColor() {
      const color = this.isochroneItem.color;
      const feature = this.selectedIsochroneFeature;
      if (color && feature) {
        feature.set("color", color);
      }
      console.log(feature);
    }
  },
  watch: {
    isochroneItem() {
      if (this.isochroneItem.id && this.isochroneLayer) {
        //Reference isochrone Feature
        this.selectedIsochroneFeature = this.isochroneLayer
          .getSource()
          .getFeatureById(this.isochroneItem.id);
      }
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
    },
    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer"
    })
  }
};
</script>
