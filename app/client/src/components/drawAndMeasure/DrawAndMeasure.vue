<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.drawAndMeasure.title") }}</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
        <v-divider></v-divider>
      </v-card-text>

      <!-- Measure -->
      <v-expansion-panels accordion>
        <v-expansion-panel readonly v-for="item in measureItems" :key="item.id">
          <v-expansion-panel-header
            expand-icon=""
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

      <v-divider></v-divider>

      <v-card-text> </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" :color="appColor.primary" @click="clear">
          <v-icon left>delete</v-icon
          >{{ $t("appBar.drawAndMeasure.clear") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
import { EventBus } from "../../EventBus";
import { Mapable } from "../../mixins/Mapable";
import { KeyShortcuts } from "../../mixins/KeyShortcuts";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";

import OlMeasureController from "../../controllers/OlMeasureController";
import { mapGetters } from "vuex";
export default {
  mixins: [InteractionsToggle, Mapable, KeyShortcuts],
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
          me.map.getTarget().style.cursor = "pointer";
          if (this.addKeyupListener) {
            this.addKeyupListener();
          }
        }
      }
    },
    doNothing() {},
    clear() {
      if (this.activeId !== undefined) {
        this.closeDrawSection();
        this.activeId = undefined;
      }
      this.stop();
      this.olMapCtrl.clear();
      this.map.getTarget().style.cursor = "";
    },
    /**
     * Stop edit and select interactions (Doesn't deletes the features)
     */
    stop() {
      const me = this;
      if (this.activeId !== undefined) {
        this.closeDrawSection();
        this.activeId = undefined;
      }
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
  mounted() {},
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    })
  }
};
</script>
<style lang="css" scoped>
.close {
  position: absolute;
  right: 10px;
  color: white;
}
.expansion-panel__container--active {
  background-color: #2bb381 !important;
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
