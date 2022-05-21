<template>
  <div>
    <v-speed-dial
      v-if="!activeId"
      v-model="measureSpeedDialFab"
      direction="right"
      class="measure-button"
      transition="slide-x-reverse-transition"
    >
      <template v-slot:activator>
        <v-btn
          v-if="!activeId"
          :color="!activeId && measureSpeedDialFab ? 'error' : appColor.primary"
          dark
          x-small
          fab
        >
          <v-icon v-if="!measureSpeedDialFab" small>
            fa-solid fa-ruler-combined
          </v-icon>
          <v-icon v-else>
            close
          </v-icon>
        </v-btn>
      </template>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-btn
            @click="
              toggle(
                { measureType: 'distance', id: 1, name: 'distance' },
                'measure'
              )
            "
            v-on="on"
            :color="appColor.primary"
            fab
            dark
            x-small
          >
            <v-icon dark>fas fa-ruler</v-icon>
          </v-btn>
        </template>
        <span>{{ $t(`appBar.drawAndMeasure.measure.length`) }}</span>
      </v-tooltip>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-btn
            @click="
              toggle({ measureType: 'area', id: 1, name: 'area' }, 'measure')
            "
            v-on="on"
            :color="appColor.primary"
            fab
            dark
            x-small
          >
            <v-icon dark>fa-solid fa-ruler-combined</v-icon>
          </v-btn>
        </template>
        <span>{{ $t(`appBar.drawAndMeasure.measure.area`) }}</span>
      </v-tooltip>
    </v-speed-dial>
    <v-btn
      class="measure-button"
      v-if="activeId"
      color="error"
      dark
      @click="stop()"
      x-small
      fab
    >
      <v-icon>
        close
      </v-icon>
    </v-btn>
  </div>
</template>
<script>
import { mapGetters } from "vuex";
import { EventBus } from "../../../../EventBus";
import { Mapable } from "../../../../mixins/Mapable";
import { KeyShortcuts } from "../../../../mixins/KeyShortcuts";
import { InteractionsToggle } from "../../../../mixins/InteractionsToggle";
import OlMeasureController from "../../../../controllers/OlMeasureController";

export default {
  name: "measure",
  mixins: [InteractionsToggle, Mapable, KeyShortcuts],
  props: {
    color: { type: String, default: "#2BB381" }
  },
  data: () => ({
    measureSpeedDialFab: false,
    interactionType: "measure-interaction",
    activeMeasureType: "",
    moduleName: "measuretool",
    stroke: "2",
    colors: {
      selected: "#3c78d8",
      exceptions: ["#FFFFFF", "#000000"]
    },
    transparency: 100,
    activeId: undefined,
    measuretoolConf: {
      strokeColor: "#ffcc33",
      fillColor: "rgba(255, 204, 51, 0.2)",
      sketchStrokeColor: "rgba(0, 0, 0, 0.5)",
      sketchFillColor: "rgba(255, 255, 255, 0.2)",
      sketchVertexStrokeColor: "rgba(0, 0, 0, 0.7)",
      sketchVertexFillColor: "rgba(255, 255, 255, 0.2)"
    }
  }),
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;
      me.olMapCtrl = new OlMeasureController(me.map, this.measuretoolConf);
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

    /**
     * Stop edit and select interactions (Doesn't deletes the features)
     */
    stop() {
      const me = this;
      this.measureSpeedDialFab = false;
      if (this.activeId !== undefined) {
        this.closeDrawSection();
        this.activeId = undefined;
      }
      me.olMapCtrl.removeInteraction();
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
      this.olMapCtrl.clear();
      this.map.getTarget().style.cursor = "";
    },
    closeDrawSection() {
      //Option only for draw section items.
      let el = this.$refs[this.activeId];
      if (el) el[0].$el.click();
    }
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
.measure-button {
  z-index: 1;
}
</style>
