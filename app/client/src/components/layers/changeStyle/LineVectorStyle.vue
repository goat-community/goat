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
      activeColor: "activeColor"
    }),
    style() {
      return this.filterStylesOnActiveModeByLayerName(
        this.item.mapLayer.get("name")
      ).rules[this.ruleIndex];
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
      this.item.layerTreeKey += 1;
    },
    resetStyle() {
      /*
        Function to reset the style of layer at attribute level
      */

      //Get original style for layer attribute
      let sourceStyle = this.$appConfig.stylesObjCopy[
        this.item.mapLayer.get("name")
      ].style.rules[this.ruleIndex];

      //Get present style for layer attribute
      let targetStyle = this.$appConfig.stylesObj[
        this.item.mapLayer.get("name")
      ].style.rules[this.ruleIndex];

      //Assign original style to present styleto reset
      targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
      targetStyle.symbolizers[0].width = sourceStyle.symbolizers[0].width;

      this.widthColor = sourceStyle.symbolizers[0].color;
      this.width = sourceStyle.symbolizers[0].width;
      this.item.mapLayer.getSource().changed();
    },
    onWidthColorChange(value) {
      //Change color of line layer on input change
      this.style.symbolizers[0].color = value.slice(0, 7);
      this.item.mapLayer.getSource().changed();
    },
    onWidthChange() {
      //Change width of line layer on input change
      if (this.width == 0) {
        this.style.symbolizers[0].width = 0.01;
      } else {
        this.style.symbolizers[0].width = this.width;
      }
      this.item.mapLayer.getSource().changed();
    }
  }
};
</script>
<style>
.v-dialog {
  box-shadow: none;
}
</style>
