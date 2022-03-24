<template>
  <span></span>
</template>
<script>
import { mapGetters } from "vuex";
import { EventBus } from "../../../../EventBus";
import { Mapable } from "../../../../mixins/Mapable";
import { getWMSLegendURL } from "../../../../utils/Layer";
import LegendRenderer from "../../../../utils/LegendRenderer";
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
      me.layers = me.map
        .getLayers()
        .getArray()
        .filter(layer => layer.get("displayInLegend") !== false);
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
        const styleObj = this.vectorTileStyles;
        const name = item.get("name");
        let styleTranslation = this.vectorTileStyles[name].translation;
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
      const style = this.vectorTileStyles[name].style;
      const filteredStyle = this.filterStylesOnActiveMode(style);
      return filteredStyle || style;
    },
    filterStylesOnActiveMode(style) {
      //get Filtered style on active mode based on style object
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
        item.get("group") !== "basemap" &&
        this.isMapMounted === true &&
        this.vectorTileStyles
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
