<template>
  <v-expansion-panels
    multiple
    v-model="panel"
    class="elevation-3"
    dark
    style="position:absolute;bottom:35px;right:10px;maxWidth: 250px;"
  >
    <v-expansion-panel
      @click="onExpansionPanelClick"
      :style="`background-color: white;`"
    >
      <v-expansion-panel-header :style="`background-color: ${color};`"
        >{{ $t("map.layerLegend.title") }}
        <template v-slot:actions>
          <v-icon small>$vuetify.icons.expand</v-icon>
        </template>
      </v-expansion-panel-header>
      <v-expansion-panel-content style="max-height:400px;">
        <vue-scroll>
          <div id="legend">
            <template v-for="(item, index) in layers">
              <div
                :key="index"
                v-if="layerVisibility(item)"
                style="padding-right:10px;"
              >
                <v-divider></v-divider>
                <!-- LAYER TITLE -->
                <p class="grey--text text--darken-2 pb-0 mb-1 mt-2 subtitle-2">
                  {{
                    $te(`map.layerName.${item.get("name")}`)
                      ? $t(`map.layerName.${item.get("name")}`)
                      : item.get("name")
                  }}
                </p>
                <!-- WMS LEGEND -->
                <div v-if="item.get('legendGraphicUrl')">
                  <img
                    crossorigin="anonymous"
                    style="max-width:100%;"
                    :src="item.get('legendGraphicUrl')"
                    class="white--text mt-0 pt-0"
                  />
                </div>
                <div v-else>
                  <div v-if="item.get('type') === 'WMS'">
                    <template
                      v-for="(layerName, index2) in item
                        .getSource()
                        .getParams()
                        .LAYERS.split(',')"
                    >
                      <div :key="index2">
                        <img
                          crossorigin="anonymous"
                          style="max-width:100%;"
                          :src="getWMSLegendImageUrl(item, layerName)"
                          class="white--text mt-0 pt-0"
                        />
                        <br />
                      </div>
                    </template>
                  </div>
                  <!-- VECTOR LEGEND -->
                  <div
                    v-if="['VECTORTILE', 'VECTOR'].includes(item.get('type'))"
                  >
                    <span
                      :ref="`legend-vector-${index}`"
                      v-html="renderLegend(item, index)"
                    ></span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </vue-scroll>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<script>
import { mapGetters } from "vuex";
import { EventBus } from "../../../../EventBus";
import { Mapable } from "../../../../mixins/Mapable";
import { getAllChildLayers, getWMSLegendURL } from "../../../../utils/Layer";
import LegendRenderer from "../../../../utils/LegendRenderer";

export default {
  mixins: [Mapable],
  name: "map-legend",
  props: {
    color: { type: String, default: "#2BB381" }
  },
  data: () => ({
    layers: [],
    panel: [],
    isMapMounted: false,
    isRendered: false
  }),
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;
      const allLayers = getAllChildLayers(me.map);
      me.layers = allLayers.filter(
        layer => layer.get("displayInLegend") !== false
      );
      this.isMapMounted = true;
      EventBus.$on("openLegend", () => this.panel.push(0));
      EventBus.$on("closeLegend", () => (this.panel = []));
    },
    getWMSLegendImageUrl(item, layerName) {
      let layerUrl = item.getSource().getUrl();
      if (layerUrl.startsWith("/")) {
        layerUrl = window.location.origin + layerUrl;
      }
      const style = item.getSource().getParams().STYLES;
      const legedUrl = getWMSLegendURL(
        layerUrl,
        layerName,
        undefined,
        undefined,
        undefined,
        undefined,
        item.getSource().serverType_,
        120,
        undefined,
        undefined,
        undefined,
        this.$i18n.locale,
        style
      );
      return legedUrl;
    },
    renderLegend(item, index) {
      setTimeout(() => {
        const styleObj = this.$appConfig.stylesObj;
        const name = item.get("name");
        let styleTranslation = this.$appConfig.stylesObj[name].translation;
        const currentLocale = this.$i18n.locale;
        if (styleObj[name] && styleObj[name].format === "geostyler") {
          let el = this.$refs[`legend-vector-${index}`];
          el = el ? el : [];
          if (el.length) {
            if (Array.isArray(el) && el.length > 0) {
              el = el[0];
            }
            // Remove existing svg elements on update (Workaround)
            if (el && el.childNodes.length > 0) {
              el.removeChild(el.childNodes[0]);
            }
            const style = styleObj[name].style;
            const filteredStyle = this.filterStylesOnActiveMode(style);

            const renderer = new LegendRenderer({
              maxColumnWidth: 240,
              overflow: "auto",
              styles: [filteredStyle || style],
              size: [230, 300],
              translation: { styleTranslation, currentLocale }
            });
            renderer.render(el);
          }
        }
      }, 100);
    },
    filterStylesOnActiveModeByLayerName(name) {
      //get Filtered style on active mode based on layer name
      const style = this.$appConfig.stylesObj[name].style;
      const filteredStyle = this.filterStylesOnActiveMode(style);
      return filteredStyle || style;
    },
    filterStylesOnActiveMode(style) {
      //get Filtered style on active mode based on style object
      const styleRules = style.rules;
      const filteredRules = [];
      const activeMode = this.calculationOptions.calculationModes.active;
      let newStyle = { ...style };
      if (Array.isArray(styleRules)) {
        styleRules.forEach(rule => {
          if (Array.isArray(rule.filter)) {
            let showInLegend = true;
            rule.filter.forEach(filter => {
              /** FILTER CURRENT MODES. */
              if (Array.isArray(filter) && filter.includes("modus")) {
                showInLegend = false;
                const operator = filter[0];
                const value = filter[2];
                if (value === activeMode && operator === "==") {
                  showInLegend = true;
                } else if (value !== activeMode && operator === "!=") {
                  showInLegend = true;
                }
              }
            });
            if (showInLegend) filteredRules.push(rule);
            // Add all other rules in the legend
          } else {
            filteredRules.push(rule);
          }
        });
        if (Array.isArray(filteredRules)) {
          newStyle.rules = filteredRules;
        }
        return newStyle;
      }
    },
    onExpansionPanelClick() {
      if (!this.isRendered) {
        this.$forceUpdate();
        this.isRendered = true;
      }
    },
    layerVisibility(item) {
      if (
        this.map.getView().getResolution() <= item.get("maxResolution") &&
        item.getVisible() === true &&
        item.get("displayInLegend") !== false &&
        item.get("group") !== "backgroundLayers" &&
        this.isMapMounted === true &&
        this.$appConfig.stylesObj
      ) {
        return true;
      }
      return false;
    }
  },

  computed: {
    ...mapGetters("isochrones", {
      calculationOptions: "options"
    })
  },
  watch: {
    "calculationOptions.calculationModes.active": function() {
      this.$forceUpdate();
    }
  }
};
</script>
<style lang="css" scoped>
.v-expansion-panel-header {
  min-height: 30px;
  padding: 5px;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 2px 0px 0px 5px;
}
</style>
