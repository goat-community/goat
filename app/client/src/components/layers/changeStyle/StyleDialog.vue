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
            <b>{{ translate("layerName", item.get("name")) }}</b>
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
          <span v-else-if="kind === `Icon`">
            <IconVectorStyle
              :item="item"
              :ruleIndex="ith"
              :key="ith"
            ></IconVectorStyle>
          </span>
        </vue-scroll>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { Draggable } from "draggable-vue-directive";
import Legend from "../../viewer/ol/controls/Legend";
import FillVectorStyle from "../changeStyle/FillVectorStyle";
import LineVectorStyle from "../changeStyle/LineVectorStyle";
import IconVectorStyle from "../changeStyle/IconVectorStyle";
import { EventBus } from "../../../EventBus";
import { getNestedProperty } from "../../../utils/Helpers";

export default {
  props: ["item", "translate", "styleDialogStatus"],
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
      appColor: "appColor"
    }),
    ...mapFields("map", {
      vectorTileStyles: "vectorTileStyles",
      vectorTileStylesCopy: "vectorTileStylesCopy"
    }),
    getItem() {
      return this.item;
    },
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
      EventBus.$emit("updateStyleDialogStatusForLayerTree", false);
      EventBus.$emit("updateStyleDialogStatusForLayerOrder", false);
      //Refresh the legend
      this.item.set("layerTreeKey", this.item.get("layerTreeKey") + 1);
    },
    onItemAttribueChange(ith) {
      this.ith = ith;
      this.kind = this.filterStylesOnActiveModeByLayerName(
        this.item.get("name")
      ).rules[ith].symbolizers[0].kind;
    }
  },
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
  }
};
</script>
<style>
.v-dialog {
  box-shadow: none;
}
</style>
