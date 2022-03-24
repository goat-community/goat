<template>
  <vue-scroll>
    <v-tabs grow v-model="tab" style="width: 400px; margin:auto;">
      <v-tab :key="1">
        <v-badge>
          <b>{{ $t("appBar.stylePanel.fillColor") }}</b>
        </v-badge>
      </v-tab>
      <v-tab :key="2">
        <v-badge>
          <b>{{ $t("appBar.stylePanel.outlineColorAndWidth") }}</b>
        </v-badge>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item :key="1">
        <v-color-picker
          class="elevation-0"
          canvas-height="100"
          width="400"
          style="margin:auto; margin-bottom: 20px;"
          :mode.sync="hexa"
          v-model="fillColor"
          @input="onFillColorChange($event)"
        >
        </v-color-picker>
      </v-tab-item>
      <v-tab-item :key="2">
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
            v-model="outLineWidth"
            :step="1"
            label="Outline Width"
            style="height:50px;"
            @input="onOutLineWidthChange()"
          ></v-text-field>
        </span>
        <v-color-picker
          class="elevation-0"
          canvas-height="100"
          width="400"
          style="margin:auto; margin-bottom: 20px;"
          :mode.sync="hexa"
          v-model="outLineColor"
          @input="onOutLineColorChange($event)"
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
import { mapFields } from "vuex-map-fields";
import Legend from "../../viewer/ol/controls/Legend";
import { debounce } from "../../../utils/Helpers";

export default {
  props: ["item", "ruleIndex"],
  mixins: [Legend],
  data: () => ({
    isExpanded: true,
    tab: null,
    hexa: "hexa",
    fillColor: null,
    outLineColor: null,
    outLineWidth: null,
    dialogue: false
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
    if (this.dialogue == true) {
      //Refresh the legend
      this.item.set("layerTreeKey", this.item.get("layerTreeKey") + 1);
    }
    this.dialogue = !this.dialogue;
    this.fillColor = this.style.symbolizers[0].color;
    this.outLineWidth = this.style.symbolizers[0].outlineWidth;
    if (this.outLineWidth == 0) {
      this.style.symbolizers[0].outlineWidth = 0.001;
      this.item.getSource().changed();
    }
    this.outLineColor = this.style.symbolizers[0].outlineColor;
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

      //Assign original style to present style to reset
      targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
      targetStyle.symbolizers[0].outlineWidth =
        sourceStyle.symbolizers[0].outlineWidth;

      targetStyle.symbolizers[0].outlineColor =
        sourceStyle.symbolizers[0].outlineColor;

      this.fillColor = targetStyle.symbolizers[0].color;
      this.outLineWidth = targetStyle.symbolizers[0].outlineWidth;
      if (this.outLineWidth == 0) {
        targetStyle.symbolizers[0].outlineWidth = 0.001;
      }
      this.outLineColor = targetStyle.symbolizers[0].outlineColor;

      this.item.getSource().changed();
    },
    updateLegendRow: debounce(function() {
      this.item.set(
        "attributeDisplayStatusKey",
        this.item.get("attributeDisplayStatusKey") + 1
      );
    }, 60),
    onFillColorChange(value) {
      //Change color of polygon fill on inpu change
      this.style.symbolizers[0].color = value.slice(0, 7);
      this.item.getSource().changed();
      this.updateLegendRow();
    },

    onOutLineColorChange(value) {
      //Change color of polygon boundary on input change
      this.style.symbolizers[0].outlineColor = value;
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    onOutLineWidthChange() {
      //Change width of Polygon boundary on input change
      if (this.outLineWidth == 0) {
        this.style.symbolizers[0].outlineWidth = 0.001;
      } else {
        this.style.symbolizers[0].outlineWidth = this.outLineWidth;
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
