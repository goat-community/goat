<template>
  <div>
    <v-btn
      class="mx-2 zoom-buttons"
      style="top:100px;"
      fab
      dark
      x-small
      color="green"
      @click="toggleFullScreen"
    >
      <v-icon medium>{{
        isFullscreen ? "fas fa-compress" : "fas fa-expand"
      }}</v-icon>
    </v-btn>
  </div>
</template>
<script>
import screenfull from "../../../../utils/ScreenFull";

export default {
  name: "full-screen",
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
