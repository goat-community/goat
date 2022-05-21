<template>
  <vue-scroll>
    <v-tabs grow v-model="tab" style="width: 400px; margin:auto;">
      <v-tab :key="1">
        <v-badge>
          <b>Change Icon Size</b>
        </v-badge>
      </v-tab>
      <v-tab :key="2">
        <v-badge>
          <b>Change Icon</b>
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
            :step="0.1"
            outlined
            tile
            v-model="iconSize"
            label="Icon Size"
            style="height:50px;"
            @input="onIconSizeChange()"
          ></v-text-field>
        </span>
      </v-tab-item>
      <v-tab-item :key="2" style="padding-top:10px;">
        <v-file-input
          append-outer-icon
          outlined
          tile
          v-model="localIcon"
          label="Local Upload"
          @change="localUpload($event)"
          style="width:300px;margin-left:50px;"
        ></v-file-input>
        <span class="d-flex mb-6" style="width:350px;">
          <v-icon style="padding-left:53px;padding-bottom:30px;font-size:20px;">
            fas fa-link
          </v-icon>
          <v-text-field
            outlined
            tile
            v-model="urlIcon"
            label="Url Upload"
            style="padding-left: 12px;"
            @input="urlUpload($event)"
          ></v-text-field>
        </span>
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
import { debounce } from "../../../utils/Helpers";
import Legend from "../../viewer/ol/controls/Legend";

export default {
  props: ["item", "ruleIndex"],
  mixins: [Legend],
  data: () => ({
    isExpanded: true,
    tab: null,
    dialogue: false,
    iconSize: null,
    urlIcon: null,
    localIcon: null
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
    this.dialogue = !this.dialogue;
    this.iconSize = this.style.symbolizers[0].size;
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

      this.urlIcon = null;
      this.localIcon = null;

      //Get original style for layer attribute
      let sourceStyle = this.vectorTileStylesCopy[this.item.get("name")].style
        .rules[this.ruleIndex];

      //Get present stylefor layer attribute
      let targetStyle = this.vectorTileStyles[this.item.get("name")].style
        .rules[this.ruleIndex];

      //Assign original style to present style to reset
      targetStyle.symbolizers[0].size = sourceStyle.symbolizers[0].size;
      targetStyle.symbolizers[0].image = sourceStyle.symbolizers[0].image;
      this.iconSize = sourceStyle.symbolizers[0].size;
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    onIconSizeChange() {
      //Change icon size on input change event
      if (this.iconSize == 0) {
        this.style.symbolizers[0].size = 0.001;
      } else {
        this.style.symbolizers[0].size = Number(this.iconSize);
      }
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    localUpload(value) {
      //Upload new icon from local
      this.urlIcon = null;
      if (value) {
        const reader = new FileReader();
        reader.readAsDataURL(value);
        reader.onload = e => {
          let icon = e.target.result;
          this.style.symbolizers[0].image = icon;
          this.item.getSource().changed();
          this.updateLegendRow();
        };
      }
    },
    urlUpload(value) {
      //Upload new icon from URL
      if (value) {
        this.style.symbolizers[0].image = value;
        this.item.getSource().changed();
        this.updateLegendRow();
      }
    }
  }
};
</script>
<style>
.v-dialog {
  box-shadow: none;
}
</style>
