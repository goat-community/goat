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
      style="position:fixed;top:10px;left:360px;z-index:2;min-width:350px;max-width:450px;height:450px;overflow:hidden;"
      v-draggable="draggableValue"
      ondragstart="return false;"
    >
      <v-layout justify-space-between column fill-height>
        <v-app-bar
          :color="appColor.primary"
          height="50"
          style="cursor:grab;"
          dark
          :ref="handleId"
        >
          <v-app-bar-nav-icon>
            <v-icon style="color:#ffffff;">
              fas fa-cog
            </v-icon>
          </v-app-bar-nav-icon>
          <v-toolbar-title>
            <div v-if="type === 'layer'">
              <b>{{ translate("layerName", item.get("name")) }}</b>
            </div>
            <div v-else>
              <v-toolbar-title>{{
                $t("isochrones.pickColor.title")
              }}</v-toolbar-title>
            </div>
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-icon @click="expand" class="toolbar-icons mr-2">
            {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}
          </v-icon>
          <v-icon @click="close" class="toolbar-icons ml-2">
            fas fa-times
          </v-icon>
        </v-app-bar>

        <vue-scroll>
          <div v-if="type === 'layer'">
            <v-select
              :items="getItemAttributes"
              @change="onItemAttribueChange($event)"
              :label="$t('appBar.stylePanel.selectAttribute')"
              outlined
              style="width:400px;margin:auto;padding-top:20px;margin-bottom:-20px"
            ></v-select>
            <span v-if="kind === `Fill`">
              <FillVectorStyle
                :item="item"
                :ruleIndex="ith"
                :key="ith"
              ></FillVectorStyle>
            </span>
            <span v-else-if="kind === `Line`">
              <LineVectorStyle
                :item="item"
                :ruleIndex="ith"
                :key="ith"
              ></LineVectorStyle>
            </span>
            <span v-else-if="kind === `Mark`">
              <IconVectorStyle
                :item="item"
                :ruleIndex="ith"
                :key="ith"
              ></IconVectorStyle>
            </span>
          </div>
          <div v-else>
            <IsochroneColorPicker
              style="margin-top: 15px"
              :temporaryColors="temporaryColors"
            />
          </div>
        </vue-scroll>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { Draggable } from "draggable-vue-directive";
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../../EventBus";
import { getNestedProperty } from "../../utils/Helpers";
import Legend from "../viewer/ol/controls/Legend.vue";
import FillVectorStyle from "../layers/changeStyle/FillVectorStyle";
import LineVectorStyle from "../layers/changeStyle/LineVectorStyle";
import IconVectorStyle from "../layers/changeStyle/IconVectorStyle.vue";
import IsochroneColorPicker from "../isochrones/IsochroneColorPicker.vue";

export default {
  props: ["type", "item", "translate", "temporaryColors"],
  mixins: [Legend],
  directives: {
    Draggable
  },
  data() {
    return {
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
    };
  },
  components: {
    FillVectorStyle,
    LineVectorStyle,
    IconVectorStyle,
    IsochroneColorPicker
  },
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
    this.isExpanded = false;
    this.isExpanded = true;
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    ...mapFields("map", {
      vectorTileStyles: "vectorTileStyles",
      vectorTileStylesCopy: "vectorTileStylesCopy"
    }),
    ...mapFields("isochrones", {
      selectedCalculationChangeColor: "selectedCalculationChangeColor"
    }),
    getItemAttributes() {
      const stylesObj = this.vectorTileStyles;
      const currentLocale = this.$i18n.locale;
      const layerName = this.item.get("name");
      return this.filterStylesOnActiveModeByLayerName(layerName).rules.map(
        (rule, i) => {
          return {
            text: getNestedProperty(
              stylesObj,
              `${layerName}.translation.${rule.name}.${currentLocale}`
            )
              ? getNestedProperty(
                  stylesObj,
                  `${layerName}.translation.${rule.name}.${currentLocale}`
                )
              : rule.name,
            value: i
          };
        }
      );
    }
  },
  methods: {
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    close() {
      if (this.type === "layer") {
        EventBus.$emit("updateStyleDialogStatusForLayerTree", false);
        EventBus.$emit("updateStyleDialogStatusForLayerOrder", false);
        this.$emit("closeTheDialog");
        //Refresh the legend
        this.item.set("layerTreeKey", this.item.get("layerTreeKey") + 1);
      } else {
        this.selectedCalculationChangeColor = null;
        // this.dialog = false;
      }
    },
    onItemAttribueChange(ith) {
      this.ith = ith;
      this.kind = this.filterStylesOnActiveModeByLayerName(
        this.item.get("name")
      ).rules[ith].symbolizers[0].kind;
    }
  }
};
</script>

<style>
.v-dialog {
  box-shadow: none;
}
</style>
