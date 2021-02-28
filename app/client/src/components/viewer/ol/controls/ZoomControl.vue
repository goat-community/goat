<template>
  <div>
    <v-tooltip right>
      <template v-slot:activator="{ on }">
        <v-btn
          class="mx-2 zoom-buttons"
          style="top:20px;"
          fab
          dark
          x-small
          :color="color"
          @click="zoom(1)"
          v-on="on"
        >
          <span style="font-size:22px;">+</span>
        </v-btn>
      </template>
      <span>{{ $t(`map.tooltips.zoomIn`) }}</span>
    </v-tooltip>
    <v-tooltip right>
      <template v-slot:activator="{ on }">
        <v-btn
          class="mx-2 zoom-buttons"
          style="top:60px;"
          fab
          dark
          x-small
          :color="color"
          @click="zoom(-1)"
          v-on="on"
        >
          <span style="font-size:22px;">−</span>
        </v-btn>
      </template>
      <span>{{ $t(`map.tooltips.zoomOut`) }}</span>
    </v-tooltip>
  </div>
</template>
<script>
import { easeOut } from "ol/easing";

export default {
  props: {
    map: { type: Object, required: true },
    color: { type: String, default: "#2BB381" }
  },
  name: "zoom-control",
  methods: {
    zoom(delta) {
      if (!this.map || !this.map.getView()) {
        return;
      }
      const view = this.map.getView();
      const currentZoom = view.getZoom();
      if (currentZoom !== undefined) {
        const newZoom = view.getConstrainedZoom(currentZoom + delta);
        if (view.getAnimating()) {
          view.cancelAnimations();
        }
        view.animate({
          zoom: newZoom,
          duration: 250,
          easing: easeOut
        });
      }
    }
  }
};
</script>
<style lang="css" scoped>
.zoom-buttons {
  position: absolute;
  left: 12px;
  z-index: 1;
}
</style>
