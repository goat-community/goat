<template>
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
          <div v-if="['GEOBUF', 'MVT'].includes(item.get('type'))">
            <span
              :ref="`legend-vector-${index}`"
              v-html="renderLegend(item, index)"
            ></span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
<script>
import { mapGetters } from "vuex";
import { EventBus } from "../../../EventBus";
import { Mapable } from "../../../mixins/Mapable";
import { getWMSLegendURL } from "../../../utils/Layer";
import LegendRenderer from "../../../utils/LegendRenderer";
import { mapFields } from "vuex-map-fields";

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
      const allLayers = me.map.getLayers().getArray();
      me.layers = allLayers.filter(layer => {
        return (
          layer.get("displayInLegend") !== false &&
          layer.get("group") !== "basemap"
        );
      });
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
      this.$nextTick(() => {
        const styleObj = this.vectorTileStyles;
        const name = item.get("name");
        let styleTranslation = styleObj[name].translation || {};
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
      });
    },
    filterStylesOnActiveMode(style) {
      const styleRules = style.rules;
      const filteredRules = [];
      const activeMode = this.calculationMode.active;
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
    layerVisibility(item) {
      if (
        (this.map.getView().getResolution() <= item.get("maxResolution") &&
          item.getVisible() === true &&
          item.get("displayInLayerList") !== false &&
          item.get("displayInLegend") !== false &&
          item.get("group") !== "backgroundLayers" &&
          this.isMapMounted === true &&
          this.vectorTileStyles) ||
        item.get("name") == "study_area_crop"
      ) {
        return true;
      }
      return false;
    }
  },

  computed: {
    ...mapGetters("app", {
      calculationMode: "calculationMode"
    }),
    ...mapFields("map", {
      vectorTileStyles: "vectorTileStyles"
    })
  },
  watch: {
    "calculationMode.active": function() {
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
