<template>
  <div>
    <div class="mb-2">
      <v-tooltip right>
        <template v-slot:activator="{ on }">
          <v-btn
            class="zoom-buttons"
            fab
            dark
            x-small
            :color="color"
            @click="zoomScreen"
            v-on="on"
          >
            <p style="margin: 0; font-size: 20px;">
              +
            </p>
          </v-btn>
        </template>

        <span>{{ $t(`map.tooltips.zoom_in`) }}</span>
      </v-tooltip>
    </div>
    <div>
      <v-tooltip right>
        <template v-slot:activator="{ on }">
          <v-btn
            class="zoom-buttons"
            fab
            dark
            x-small
            :color="color"
            @click="zoomOut"
            v-on="on"
          >
            <p class="text-h5" style="margin: 0; font-size: 20px;">
              -
            </p>
          </v-btn>
        </template>

        <span>{{ $t(`map.tooltips.zoom_out`) }}</span>
      </v-tooltip>
    </div>
  </div>
</template>
<script>
import { Mapable } from "../../../../mixins/Mapable";

export default {
  mixins: [Mapable],
  name: "zoom",
  props: {
    color: { type: String, default: "#2BB381" }
  },
  data: () => ({
    isFullscreen: false
  }),
  methods: {
    /**
     * Switch to/from fullscreen mode.
     * Must be triggered by mouse event
     */
    zoomScreen() {
      var view = this.map.getView();
      var zoom = view.getZoom();
      // view.setZoom(zoom + 0.5);
      view.animate({
        zoom: zoom + 0.5,
        duration: 300 // animation duration in milliseconds
      });
    },
    zoomOut() {
      var view = this.map.getView();
      var zoom = view.getZoom();
      // view.setZoom(zoom - 0.5);
      view.animate({
        zoom: zoom - 0.5,
        duration: 300 // animation duration in milliseconds
      });
    }
  }
};
</script>
<style lang="css" scoped>
.zoom-buttons {
  z-index: 1;
}
</style>
