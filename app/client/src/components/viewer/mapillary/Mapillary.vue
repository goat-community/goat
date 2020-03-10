<template>
  <div id="mapillary-container"></div>
</template>
<script>
import { Viewer } from "mapillary-js";

import "mapillary-js/dist/mapillary.min.css";

export default {
  name: "app-mapillary",
  data() {
    return {
      mapillary: null
    };
  },
  mounted() {
    const clientId = "MkJKbDA0bnZuZlcxeTJHTmFqN3g1dzo1YTM0NjRkM2EyZGU5MzBh";
    const key = "rrKZdmgdvup_KYJKTESq0Q";

    // var urlStartImage = `https://a.mapillary.com/v3/images/${key}?client_id=${clientId}`;
    // var urlSequence = `https://a.mapillary.com/v3/sequences/JMOBN38RSF2h6dpuuiBz6w?client_id=${clientId}`;

    // var imagesUrl = `https://a.mapillary.com/v3/images?client_id=${clientId}&sequence_keys=JMOBN38RSF2h6dpuuiBz6w`;

    this.mapillary = new Viewer("mapillary-container", clientId, key, {
      component: { cover: false }
    });

    window.addEventListener("resize", () => {
      this.mapillary.resize();
    });
  }
};
</script>
<style lang="css" scoped></style>
