<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.drawAndMeasure.title") }}</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
        <v-divider></v-divider>
      </v-card-text>
      <v-subheader
        ><h3>{{ $t("appBar.drawAndMeasure.measure.header") }}</h3>
      </v-subheader>

      <!-- Measure -->
      <v-expansion-panels accordion>
        <v-expansion-panel readonly v-for="item in measureItems" :key="item.id">
          <v-expansion-panel-header
            expand-icon=""
            v-slot="{ open }"
            :class="{
              'expansion-panel__container--active': activeId === item.id
            }"
            @click="toggle(item, 'measure')"
          >
            <v-layout row>
              <v-flex xs2>
                <v-icon
                  small
                  left
                  :class="{ activeIcon: activeId === item.id }"
                  >{{ item.icon }}</v-icon
                >
              </v-flex>
              <v-flex xs10>
                <span>{{
                  $t(`appBar.drawAndMeasure.measure.${item.name}`)
                }}</span>
              </v-flex>
            </v-layout>
          </v-expansion-panel-header>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Draw -->
      <!-- <v-subheader>
        <h3>{{ $t("appBar.drawAndMeasure.draw.header") }}</h3>
      </v-subheader>
      <v-divider></v-divider>
      <v-expansion-panel accordion>
        <v-expansion-panel v-for="item in drawItems" :key="item.id">
          <v-expansion-panel-header
            class="elevation-1"
            expand-icon=""
            v-slot="{ open }"
          >
            <v-layout row>
              <v-flex xs2>
                <v-icon
                  small
                  left
                  :class="{ activeIcon: activeId === item.id }"
                  >{{ item.icon }}</v-icon
                >
              </v-flex>
              <v-flex xs8>
                <span>{{ item.text }}</span>
              </v-flex>
              <v-flex xs2>
                <v-icon class="close" v-bind:ref="item.id">{{
                  activeId === item.id ? "close" : ""
                }}</v-icon>
              </v-flex>
            </v-layout>
          </v-expansion-panel-header>
          <v-expansion-panel-content
            :class="{
              'expansion-panel__container--active': activeId === item.id
            }"
            @click.native="toggle(item.id, 'draw')"
          >
            <v-card @click.stop="doNothing" class="card">
              <v-card-text>
               
                <v-layout row wrap align-center class="ml-3">
                  <v-flex xs4>
                    <span>{{ $t("appBar.drawAndMeasure.draw.color") }}</span>
                  </v-flex>
                  <v-flex xs8>
                    <swatches
                      @input="colorChange"
                      class="ml-3"
                      v-model="colors.selected"
                      colors="text-advanced"
                      swatch-size="24"
                      popover-to="left"
                      :exceptions="colors.exceptions"
                    ></swatches>
                  </v-flex>
                </v-layout>

             
                <v-layout row wrap align-center class="ml-3">
                  <v-flex xs4>
                    <span>{{
                      $t("appBar.drawAndMeasure.draw.transparency")
                    }}</span>
                  </v-flex>
                  <v-flex xs8 class="pl-4 pr-3">
                    <v-slider
                      v-model="transparency"
                      @change="transparencyChange"
                      min="1"
                      max="100"
                    ></v-slider>
                  </v-flex>
                </v-layout>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panel> -->

      <v-divider></v-divider>

      <v-card-text> </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" color="green" @click="clear">
          <v-icon left>delete</v-icon
          >{{ $t("appBar.drawAndMeasure.clear") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
// import Swatches from "vue-swatches";
import "vue-swatches/dist/vue-swatches.min.css";

import { EventBus } from "../../EventBus";
import { Mapable } from "../../mixins/Mapable";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";

import OlMeasureController from "../../controllers/OlMeasureController";

export default {
  mixins: [InteractionsToggle, Mapable],
  data: () => ({
    interactionType: "measure-interaction",
    activeMeasureType: "",
    moduleName: "measuretool",
    stroke: "2",
    colors: {
      selected: "#3c78d8",
      exceptions: ["#FFFFFF", "#000000"]
    },
    transparency: 100,
    measureItems: [
      {
        id: 1,
        icon: "fas fa-ruler",
        name: "length", //this.$t("appBar.drawAndMeasure.measure.length")
        measureType: "distance"
      },
      {
        id: 2,
        icon: "fas fa-ruler-combined",
        name: "area",
        measureType: "area"
      }
    ],
    drawItems: [
      {
        id: 3,
        icon: "far fa-dot-circle",
        name: "point"
      },
      {
        id: 4,
        icon: "fas fa-dot-circle",
        name: "pointWithCoord"
      },
      {
        id: 5,
        icon: "fas fa-project-diagram",
        name: "line"
      },
      {
        id: 6,
        icon: "fas fa-draw-polygon",
        name: "polygon"
      },
      {
        id: 7,
        icon: "fas fa-font",
        name: "label"
      }
    ],
    activeId: undefined
  }),
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;
      const measureConf = me.$appConfig.map.modules[me.moduleName] || {};
      me.olMapCtrl = new OlMeasureController(me.map, measureConf);
      me.olMapCtrl.createMeasureLayer();
    },
    toggle(item, type) {
      const me = this;

      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", me.interactionType);

      //1- Set active index of clicked item or remove it
      //- If type is measure  toggle off drawing section if opened
      me.olMapCtrl.removeInteraction();

      const id = item.id;
      if (type === "measure") {
        me.closeDrawSection();
        if (me.activeId === id) {
          me.activeId = undefined;
          me.activeMeasureType = "";
        } else {
          this.activeId = id;
          me.olMapCtrl.addInteraction(item.measureType);
          me.activeMeasureType = item.measureType;
        }
      }
    },
    doNothing() {},
    clear() {
      if (this.activeId !== undefined) {
        this.closeDrawSection();
        this.activeId = undefined;
      }
      this.olMapCtrl.clear();
    },
    /**
     * Stop edit and select interactions (Doesn't deletes the features)
     */
    stop() {
      const me = this;
      me.olMapCtrl.removeInteraction();
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
    },
    closeDrawSection() {
      //Option only for draw section items.
      let el = this.$refs[this.activeId];
      if (el) el[0].$el.click();
    },
    colorChange() {},
    transparencyChange() {}
  },
  mounted() {}
};
</script>
<style lang="css" scoped>
.close {
  position: absolute;
  right: 10px;
  color: white;
}
.expansion-panel__container--active {
  background-color: #4caf50 !important;
  color: white !important;
  font-weight: bold !important;
}
.card {
  font-weight: normal !important;
}
.activeIcon {
  font-size: 20px;
  color: white;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0px;
}
</style>
