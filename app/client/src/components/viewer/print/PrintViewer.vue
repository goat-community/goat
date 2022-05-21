<template>
  <div>
    <v-row align="center">
      <div
        id="map-print-wrapper"
        class="elevation-10 ml-4 ma-3"
        :style="
          `position:relative;width:${print.layout.size[0]}mm;height:${print.layout.size[1]}mm;padding:${print.layout.padding}mm;`
        "
      >
        <!-- MAP -->
        <div
          :style="
            `width:${getMapWidth}mm;height:${getMapHeight}mm;position:absolute;border: 1px solid #ccc;`
          "
          id="ol-map-print"
        >
          <img
            crossorigin="anonymous"
            :src="rotationIcon"
            :style="
              `transform:rotate(${print.rotation}deg);z-index:2;max-width:10mm;position:absolute;right:5mm;top:5mm;`
            "
          />
          <!-- TIME -->
          <div
            class="caption"
            :style="
              `z-index:1;position:absolute;left:0mm;bottom:-5mm;font-size:0.55rem !important;`
            "
          >
            {{ `CRS: ${print.selectedCrs}` }}
          </div>
          <!-- CRS -->
          <div
            class="caption"
            :style="
              `z-index:1;max-width:40mm;position:absolute;right:0mm;bottom:-5mm;font-size:0.55rem !important;`
            "
          >
            {{ formatedDateTime }}
          </div>
        </div>

        <!-- TITLE -->
        <div class="title" ref="print-title" :style="getTitleStyle">
          {{ print.title ? print.title.toUpperCase() : "" }}
        </div>
        <!-- LEGEND -->
        <div
          v-if="print.legend"
          :style="
            getLegendStyle() + `max-height:${this.getLegendMaxHeight()}mm;`
          "
        >
          <div class=".subtitle-1">LEGEND</div>

          <print-legend v-if="print.active === true"></print-legend>
        </div>
        <!-- GOAT LOGO -->
        <img
          crossorigin="anonymous"
          :src="logoGoat"
          :style="
            `z-index:1;max-width:30mm;position:absolute;right:39mm;bottom:5mm;padding-right:2mm;border-right: 1px solid #ccc;`
          "
        />
        <img
          crossorigin="anonymous"
          :src="logoP4B"
          :style="
            `z-index:1;max-width:35mm;position:absolute;right:2mm;bottom:5mm;`
          "
        />
      </div>
    </v-row>
  </div>
</template>
<script>
import { mapGetters } from "vuex";
import { getCurrentDate, getCurrentTime } from "../../../utils/Helpers";
import PrintLegend from "./PrintLegend";
import { Mapable } from "../../../mixins/Mapable";
export default {
  components: {
    "print-legend": PrintLegend
  },
  mixins: [Mapable],
  data() {
    return {
      mapSideSheetSize: 65, // in mm. The sheet area for legend, title and logos. (right or bottom)
      logoGoat: "img/goat_standard.svg",
      logoP4B: "img/plan4better_standard.svg",
      rotationIcon: "img/north_arrow.png"
    };
  },
  computed: {
    ...mapGetters("map", {
      print: "print"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    /**
     * Get formated date time as dd/mm/yyyy hh:mm:ss
     */
    formatedDateTime() {
      const m = new Date();
      const dateString =
        m.getUTCFullYear() +
        "/" +
        ("0" + (m.getUTCMonth() + 1)).slice(-2) +
        "/" +
        ("0" + m.getUTCDate()).slice(-2) +
        " " +
        ("0" + m.getUTCHours()).slice(-2) +
        ":" +
        ("0" + m.getUTCMinutes()).slice(-2) +
        ":" +
        ("0" + m.getUTCSeconds()).slice(-2);
      return dateString;
    },
    /**
     * Map viewport width in mm
     */
    getMapWidth() {
      const sheetWidth = this.print.layout.size[0];
      const sheetPadding = this.print.layout.padding;
      let viewPortWidth = sheetWidth - 2 * sheetPadding;
      if (this.print.layout.orientation === "landscape" && this.print.legend) {
        viewPortWidth = viewPortWidth - this.mapSideSheetSize;
      }
      return viewPortWidth;
    },
    /**
     * Map viewport height in mm
     */
    getMapHeight() {
      const sheetHeight = this.print.layout.size[1];
      const sheetPadding = this.print.layout.padding;
      let viewPortHeight = sheetHeight - 2 * sheetPadding;
      if (this.print.layout.orientation === "portrait" && this.print.legend) {
        viewPortHeight = viewPortHeight - this.mapSideSheetSize;
      }
      // If legend is deactivated, create a small sheet padding in the bottom to position title and logos
      if (!this.print.legend) {
        viewPortHeight = viewPortHeight - 20;
      }
      return viewPortHeight;
    },
    /**
     * Get title style based on layout size, orientation and legend visibility
     */
    getTitleStyle() {
      let left;
      let top;
      const sheetWidth = this.print.layout.size[0];
      const sheetPadding = this.print.layout.padding;
      if (this.print.legend && this.print.layout.orientation === "landscape") {
        left = 5 + sheetPadding + this.getMapWidth;
        top = sheetPadding;
      } else {
        left = sheetWidth / 2 - 30;
        top = sheetPadding + this.getMapHeight;
      }
      const style = `z-index: 1;width: 60mm;text-align: center;word-wrap: break-word;vertical-align: middle;position:absolute;left:${left}mm;top:${top}mm;`;
      return style;
    }
  },
  watch: {
    "print.active": function(state) {
      if (state === true) {
        this.map.setTarget("ol-map-print");
      } else {
        this.map.setTarget("ol-map-container");
      }
    },
    "print.layout": function() {
      this.updateMap();
    },
    "print.legend": function() {
      this.updateMap();
    },
    "print.title": function(newValue, oldValue) {
      // Rerender if user clear the text
      if (!newValue || newValue.length - oldValue.length > 1) {
        setTimeout(() => {
          this.$forceUpdate();
        }, 50);
      }
    }
  },
  methods: {
    getCurrentDate,
    getCurrentTime,
    updateMap() {
      // Workaround as we have for the map to be rendered.
      setTimeout(() => {
        this.map.updateSize();
        this.map.render();
      }, 50);
    },
    /**
     * Legend style
     */
    getLegendStyle() {
      let left;
      let top;
      const padding = this.print.layout.padding;
      if (this.print.layout.orientation === "portrait") {
        left = padding;
        top = padding + this.getMapHeight + 7; // 7 is added to avoid overlapping with crs label
      } else {
        left = 5 + padding + this.getMapWidth;
        const title = this.$refs["print-title"];
        if (title && title.clientHeight) {
          console.log(title.clientHeight);
          let pixels = padding + title.clientHeight;
          top = (pixels * 25.4) / 72 + 7; // convert to mm
        } else {
          top = padding;
        }
      }
      const style = `z-index:1;position:absolute;top:${top}mm;left:${left}mm;overflow:hidden;`;
      return style;
    },
    /**
     * Legend Height
     */
    getLegendMaxHeight() {
      let maxHeight;
      const padding = this.print.layout.padding;
      if (this.print.layout.orientation === "landscape") {
        maxHeight = this.print.layout.size[1] - 2 * padding - 10;
      } else {
        maxHeight =
          this.print.layout.size[1] - 2 * padding - this.getMapHeight - 5;
      }
      return maxHeight;
    }
  }
};
</script>
