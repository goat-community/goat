<template>
  <v-dialog
    width="300"
    overlay-opacity="0"
    persistent
    no-click-animation
    hide-overlay
    v-model="dialogue"
    content-class="v-dialog"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-icon
        v-ripple
        style="color:#B0B0B0;margin-bottom:15px;cursor:pointer"
        dark
        v-bind="attrs"
        v-on="on"
        @click="onSettingClick()"
      >
        fas fa-cog
      </v-icon>
    </template>
    <v-card
      class="mx-auto"
      :style="[isExpanded ? { height: 'auto' } : { height: '50px' }]"
      style="position:fixed;top:10px;left:360px;z-index:2;max-width:350px;min-width:450px;height:450px;overflow:hidden;"
    >
      <v-layout justify-space-between column fill-height>
        <v-app-bar
          :color="activeColor.primary"
          height="50"
          style="cursor:grab;"
          dark
        >
          <v-app-bar-nav-icon>
            <v-icon style="color:#B0B0B0;">
              fas fa-cog
            </v-icon>
          </v-app-bar-nav-icon>
          <v-toolbar-title><b>Style Setting</b></v-toolbar-title>
          <v-spacer></v-spacer>
          <v-icon @click="expand" class="toolbar-icons mr-2">
            {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}
          </v-icon>
          <v-icon @click="close" class="toolbar-icons ml-2">
            fas fa-times
          </v-icon>
        </v-app-bar>
        <vue-scroll>
          <v-tabs grow v-model="tab">
            <v-tab :key="1">
              <v-badge>
                <b>Width & Width Color</b>
              </v-badge>
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-tab-item :key="1">
              <span class="d-flex mb-6" style="margin:10px 20px 0px 20px;">
                <v-text-field
                  type="number"
                  :min="0"
                  outlined
                  tile
                  v-model="width"
                  :step="stepSize"
                  label="Layer Width"
                  style="height:50px;width:100px !important;margin-right:50px;"
                  @input="onWidthChange()"
                ></v-text-field>
                <v-text-field
                  type="number"
                  :min="1"
                  outlined
                  tile
                  v-model="stepSize"
                  label="Step Size"
                  style="height:50px;width:100px !important;margin-right:50px;"
                ></v-text-field>
              </span>
              <v-color-picker
                width="400"
                style="margin:auto"
                :mode.sync="hexa"
                v-model="widthColor"
                @input="onWidthColorChange($event)"
              >
              </v-color-picker>
            </v-tab-item>
          </v-tabs-items>
        </vue-scroll>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { Draggable } from "draggable-vue-directive";
import Legend from "../../viewer/ol/controls/Legend";

export default {
  props: ["item", "ruleIndex"],
  mixins: [Legend],
  directives: {
    Draggable
  },
  data: () => ({
    isExpanded: true,
    tab: null,
    hexa: "hexa",
    widthColor: null,
    width: null,
    dialogue: false,
    stepSize: 1
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
  methods: {
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    close() {
      this.dialogue = false;
      //Refresh the legend
      this.item.layerTreeKey += 1;
    },
    onSettingClick() {
      if (this.dialogue == true) {
        //Refresh the legend
        this.item.layerTreeKey += 1;
      }
      this.dialogue = !this.dialogue;
      this.widthColor = this.style.symbolizers[0].color;
      this.width = this.style.symbolizers[0].width;
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
