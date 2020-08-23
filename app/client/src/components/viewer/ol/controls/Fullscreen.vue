<template>
  <div>
    <v-tooltip right>
      <template v-slot:activator="{ on }">
        <v-btn
          class="mx-2 zoom-buttons"
          style="top:100px;"
          fab
          dark
          x-small
          :color="color"
          @click="toggleFullScreen"
          v-on="on"
        >
          <v-icon medium>{{
            isFullscreen ? "fas fa-compress" : "fas fa-expand"
          }}</v-icon>
        </v-btn>
      </template>

      <span>{{
        $t(`map.tooltips.${isFullscreen ? "exitFullScreen" : "openFullScreen"}`)
      }}</span>
    </v-tooltip>
  </div>
</template>
<script>
import screenfull from "../../../../utils/ScreenFull";

export default {
  name: "full-screen",
  props: {
    color: { type: String, default: "#4CAF50" }
  },
  data: () => ({
    isFullscreen: false
  }),
  methods: {
    /**
     * Switch to/from fullscreen mode.
     * Must be triggered by mouse event
     */
    toggleFullScreen() {
      if (screenfull.isEnabled) {
        screenfull.toggle();
      }
    }
  },

  mounted() {
    screenfull.on("change", () => {
      this.isFullscreen = screenfull.isFullscreen;
    });
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
