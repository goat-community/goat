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
          <b>{{ $t("appBar.stylePanel.iconSize") }}</b>
        </v-badge>
      </v-tab>
      <v-tab :key="3">
        <v-badge>
          <b>{{ $t("appBar.stylePanel.changeIcon") }}</b>
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
            :step="0.1"
            outlined
            tile
            v-model="iconSize"
            label="Icon Size"
            style="height:50px;"
            @change="onIconSizeChange()"
          ></v-text-field>
        </span>
      </v-tab-item>
      <v-tab-item :key="3" style="padding-top:10px;">
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
import { Icon, Style } from "ol/style";
import Fill from "ol/style/Fill";
import Circle from "ol/style/Circle";

export default {
  props: ["item", "ruleIndex"],
  mixins: [Legend],
  data: () => ({
    isExpanded: true,
    tab: null,
    fillColor: null,
    dialogue: false,
    iconSize: null,
    urlIcon: null,
    hexa: "hexa",
    localIcon: null,
    iconStyle: null,
    activeStyle: "square",
    currentIcon: null,
    defaultColor: null
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
    this.fillColor = this.style.symbolizers[0].color;
    this.defaultColor = this.style.symbolizers[0].color;
  },
  mounted() {
    this.iconSize = this.style.symbolizers[0].radius;
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

      this.style.symbolizers[0].color = this.defaultColor;
      this.updateLayer(3);

      //Assign original style to present style to reset
      targetStyle.symbolizers[0].size = sourceStyle.symbolizers[0].size;
      targetStyle.symbolizers[0].image = sourceStyle.symbolizers[0].image;
      this.iconSize = sourceStyle.symbolizers[0].size;
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    onFillColorChange(value) {
      this.style.symbolizers[0].color = value;
      this.item.getSource().changed();
      this.updateLegendRow();
      this.updateLayer(this.style.symbolizers[0].radius);
    },
    updateLayer(rasiusSize) {
      this.activeStyle = "square";
      this.normalLayer = new Style({
        image: new Circle({
          fill: new Fill({
            color: this.style.symbolizers[0].color
          }),
          radius: rasiusSize,
          kind: "Mark",
          wellKnownName: "Square",
          title: "square"
        })
      });
      this.item.setStyle(this.normalLayer);
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    updateIcon(radiusSize) {
      this.activeStyle = "image";
      this.iconStyle = new Style({
        image: new Icon({
          anchor: [0.5, 46],
          anchorXUnits: "fraction",
          anchorYUnits: "pixels",
          scale: radiusSize,
          src: this.currentIcon,
          title: "image"
        })
      });

      this.item.setStyle(this.iconStyle);
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    updateUrlIcon(radiusSize) {
      this.activeStyle = "image";
      this.iconStyle = new Style({
        image: new Icon({
          anchor: [0.5, 46],
          anchorXUnits: "fraction",
          anchorYUnits: "pixels",
          scale: radiusSize,
          src: this.urlIcon,
          title: "image"
        })
      });
      this.activeStyle = "imageUrl";

      this.item.setStyle(this.iconStyle);
      this.item.getSource().changed();
      this.updateLegendRow();
    },
    onIconSizeChange() {
      //Change icon size on input change event

      if (this.iconSize == 0) {
        if (this.activeStyle === "square") {
          this.updateLayer(0.001);
        } else if (this.activeStyle === "image") {
          this.updateIcon(0.001);
        } else {
          this.updateUrlIcon(0.001);
        }
        this.style.symbolizers[0].radius = 0.001;
      } else {
        if (this.activeStyle === "square") {
          this.updateLayer(this.iconSize);
        } else if (this.activeStyle === "image") {
          this.updateIcon(this.iconSize);
        } else {
          this.updateUrlIcon(this.iconSize);
        }
        this.style.symbolizers[0].radius = Number(this.iconSize);
      }
    },
    localUpload(value) {
      //Upload new icon from local

      this.urlIcon = null;
      if (value) {
        const reader = new FileReader();
        reader.readAsDataURL(value);
        reader.onload = e => {
          this.currentIcon = e.target.result;
          this.style.symbolizers[0].radius = 0.05;

          this.iconStyle = new Style({
            image: new Icon({
              anchor: [0.5, 46],
              anchorXUnits: "fraction",
              anchorYUnits: "pixels",
              scale: this.style.symbolizers[0].radius,
              src: this.currentIcon,
              title: "image"
            })
          });
          this.activeStyle = "image";

          this.item.setStyle(this.iconStyle);
          this.item.getSource().changed();
          this.updateLegendRow();
        };
      } else {
        this.style.symbolizers[0].radius = 3;
        this.updateLayer(this.style.symbolizers[0].radius);
      }
    },
    urlUpload(value) {
      //Upload new icon from URL
      if (value) {
        this.style.symbolizers[0].radius = 0.05;

        this.iconStyle = new Style({
          image: new Icon({
            anchor: [0.5, 46],
            anchorXUnits: "fraction",
            anchorYUnits: "pixels",
            scale: this.style.symbolizers[0].radius,
            src: this.urlIcon,
            title: "image"
          })
        });
        this.activeStyle = "imageUrl";

        this.item.setStyle(this.iconStyle);
        this.item.getSource().changed();
        this.updateLegendRow();
      } else {
        this.style.symbolizers[0].radius = 3;
        this.updateLayer(this.style.symbolizers[0].radius);
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
