<template>
  <v-dialog
    width="300"
    overlay-opacity="0"
    persistent
    no-click-animation
    hide-overlay
    v-model="dialog"
    content-class="v-dialog"
  >
    <v-card
      :style="[isExpanded ? { height: 'auto' } : { height: '50px' }]"
      style="
        position: fixed;
        top: 10px;
        left: 360px;
        z-index: 2;
        min-width: 350px;
        max-width: 450px;
        height: 450px;
        overflow: hidden;
      "
      v-draggable="draggableValue"
      ondragstart="return false;"
    >
      <v-layout justify-space-between column fill-height>
        <v-app-bar
          :color="activeColor.primary"
          height="50"
          style="cursor: grab"
          dark
          :ref="handleId"
        >
          <v-app-bar-nav-icon>
            <v-icon style="color: #ffffff"> fas fa-cog </v-icon>
          </v-app-bar-nav-icon>
          <v-toolbar-title>
            <b>{{ attr_name() }} - {{ translate("layerName", item.name) }}</b>
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-icon
            @click="resetStyle"
            class="toolbar-icons mr-2"
            style="cursor: pointer"
          >
            fas fa-sync-alt
          </v-icon>
          <v-icon @click="expand" class="toolbar-icons mr-2">
            {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}
          </v-icon>
          <v-icon @click="close" class="toolbar-icons ml-2">
            fas fa-times
          </v-icon>
        </v-app-bar>
        <vue-scroll>
          <span v-if="kind === `Fill`">
            <FillVectorStyle
              :item="item"
              :ruleIndex="ruleIndex"
              :key="ruleIndex"
            ></FillVectorStyle>
          </span>
          <span v-else-if="kind === `Line`">
            <LineVectorStyle
              :item="item"
              :ruleIndex="ruleIndex"
              :key="ruleIndex"
            ></LineVectorStyle>
          </span>
          <span v-else-if="kind === `Icon`">
            <IconVectorStyle
              :item="item"
              :ruleIndex="ruleIndex"
              :key="ruleIndex"
            ></IconVectorStyle>
          </span>
        </vue-scroll>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { Draggable } from "draggable-vue-directive";
import Legend from "../../viewer/ol/controls/Legend";
import FillVectorStyle from "../changeStyle/FillVectorStyle";
import LineVectorStyle from "../changeStyle/LineVectorStyle";
import IconVectorStyle from "../changeStyle/IconVectorStyle";
import { EventBus } from "../../../EventBus";

export default {
  props: ["item", "translate", "styleDialogStatus", "ruleIndex"],
  mixins: [Legend],
  directives: {
    Draggable
  },
  data: () => ({
    isExpanded: true,
    tab: null,
    dialog: true,
    kind: null,
    ith: null,
    handleId: "handle-id",
    draggableValue: {
      handle: undefined,
      boundingElement: undefined,
      resetInitialPos: undefined
    }
  }),
  components: {
    FillVectorStyle,
    LineVectorStyle,
    IconVectorStyle
  },
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    getItem() {
      return this.item;
    }
  },
  methods: {
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    attr_name() {
      let curr_style = this.filterStylesOnActiveModeByLayerName(
        this.item.mapLayer.get("name")
      ).rules[this.ruleIndex];
      if (
        this.$appConfig.stylesObj[this.item.mapLayer.get("name")]
          .translation === undefined
      ) {
        return curr_style.name;
      }
      return this.$appConfig.stylesObj[this.item.mapLayer.get("name")]
        .translation[curr_style.name][this.$i18n.locale];
    },
    close() {
      EventBus.$emit("updateStyleDialogStatusForLayerTree", false);
      EventBus.$emit("updateStyleDialogStatusForLayerOrder", false);
      //Refresh the legend
      this.item.layerTreeKey += 1;
    },
    resetStyle() {
      /*
        Function to reset the style of layer at attribute level
      */
      //Get original style for layer attribute
      let sourceStyle = this.filterStylesOnActiveModeByLayerName(
        this.item.mapLayer.get("name"),
        true
      ).rules[this.ruleIndex];

      //Get present style for layer attribute
      let targetStyle = this.filterStylesOnActiveModeByLayerName(
        this.item.mapLayer.get("name")
      ).rules[this.ruleIndex];
      if (this.kind === "Fill") {
        //Assign original style to present style to reset
        targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
        targetStyle.symbolizers[0].outlineWidth =
          sourceStyle.symbolizers[0].outlineWidth;
        targetStyle.symbolizers[0].outlineColor =
          sourceStyle.symbolizers[0].outlineColor;
      } else if (this.kind === "Line") {
        //Assign original style to present style to reset
        targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
        targetStyle.symbolizers[0].width = sourceStyle.symbolizers[0].width;
      } else if (this.kind === "Icon") {
        //Assign original style to present style to reset
        targetStyle.symbolizers[0].size = sourceStyle.symbolizers[0].size;
        targetStyle.symbolizers[0].image = sourceStyle.symbolizers[0].image;
      }
      this.item.mapLayer.getSource().changed();
      this.item.styleComponentResetKey += 1;
    }
  },
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
    let curr_style = this.filterStylesOnActiveModeByLayerName(
      this.item.mapLayer.get("name")
    ).rules[this.ruleIndex];
    this.kind = curr_style.symbolizers[0].kind;
  }
};
</script>
<style>
.v-dialog {
  box-shadow: none;
}
</style>
