<template>
  <vue-scroll>
    <v-tabs grow v-model="tab" style="width: 400px; margin:auto;">
      <v-tab :key="1">
        <v-badge>
          <b>Width & Width Color</b>
        </v-badge>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item :key="1">
        <span
          class="d-flex mb-6"
          style="width:400px;margin:10px auto 0px auto;"
        >
          <v-text-field
            type="number"
            :min="0"
            :max="10"
            outlined
            tile
            v-model="width"
            :step="1"
            label="Layer Width"
            style="height:50px;"
            @input="onWidthChange()"
          ></v-text-field>
        </span>
        <v-color-picker
          class="elevation-0"
          canvas-height="100"
          width="400"
          style="margin:auto; margin-bottom: 20px;"
          :mode.sync="hexa"
          v-model="widthColor"
          @input="onWidthColorChange($event)"
        >
        </v-color-picker>
      </v-tab-item>
    </v-tabs-items>
    <v-btn
      color="warning"
      dark
      @click="resetStyle"
      style="width:100%;background-color: #2bb381 !important;"
    >
      Reset Style
    </v-btn>
  </vue-scroll>
</template>

<script>
import { mapGetters } from "vuex";
import Legend from "../../viewer/ol/controls/Legend";
import { mapFields } from "vuex-map-fields";
import { debounce } from "../../../utils/Helpers";
export default {
  props: ["item", "ruleIndex"],
  mixins: [Legend],
  data: () => ({
    isExpanded: true,
    tab: null,
    hexa: "hexa",
    widthColor: null,
    width: null
  }),
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    ...mapFields("map", {
      vectorTileStyles: "vectorTileStyles",
      vectorTileStylesCopy: "vectorTileStylesCopy"
    }),
    style() {
      return this.filterStylesOnActiveModeByLayerName(this.item.get("name"))
        .rules[this.ruleIndex];
    }
  },
  created() {
    this.widthColor = this.style.symbolizers[0].color;
    this.width = this.style.symbolizers[0].width;
  },
  methods: {
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    close() {
      this.dialogue = false;
      //Refresh the legend
      this.item.set("layerTreeKey", this.item.get("layerTreeKey") + 1);
    },
    updateLegendRow: debounce(function() {
      this.item.set(
        "attributeDisplayStatusKey",
        this.item.get("attributeDisplayStatusKey") + 1
      );
    }, 60),
    resetStyle() {
      /*
        Function to reset the style of layer at attribute level
      */

      //Get original style for layer attribute
      let sourceStyle = this.vectorTileStylesCopy[this.item.get("name")].style
        .rules[this.ruleIndex];

      //Get present style for layer attribute
      let targetStyle = this.vectorTileStyles[this.item.get("name")].style
        .rules[this.ruleIndex];

      //Assign original style to present styleto reset
      targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
      targetStyle.symbolizers[0].width = sourceStyle.symbolizers[0].width;

      this.widthColor = sourceStyle.symbolizers[0].color;
      this.width = sourceStyle.symbolizers[0].width;
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    onWidthColorChange(value) {
      //Change color of line layer on input change
      this.style.symbolizers[0].color = value.slice(0, 7);
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    onWidthChange() {
      //Change width of line layer on input change
      if (this.width == 0) {
        this.style.symbolizers[0].width = 0.01;
      } else {
        this.style.symbolizers[0].width = this.width;
      }
      this.item.getSource().changed();
      this.updateLegendRow();
    }
  }
};
</script>
<style>
.v-dialog {
  box-shadow: none;
}
</style>
