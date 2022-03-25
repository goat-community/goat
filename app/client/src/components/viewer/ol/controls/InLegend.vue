<template>
  <div>
    <div
      v-if="
        layer.get('legendGraphicUrls') &&
          Array.isArray(layer.get('legendGraphicUrls'))
      "
    >
      <template
        v-for="(legendUrl, indexLegendUrls) in layer.get('legendGraphicUrls')"
      >
        <div :key="indexLegendUrls">
          <img
            crossorigin="anonymous"
            style="max-width:100%; padding-left:50px;"
            :src="legendUrl"
            class="white--text mt-0 pt-0"
          />
        </div>
      </template>
    </div>
    <div v-else>
      <div :key="legendRerenderOnActiveMode">
        <div
          v-if="
            vectorTileStyles[layer.get('name')] &&
              ['VECTOR', 'GEOBUF', 'MVT'].includes(
                layer.get('type').toUpperCase()
              )
          "
          style="text-align: center; padding: 20px;"
          :key="layer.get('layerTreeKey')"
        >
          <div v-if="vectorTileStyles[layer.get('name')]">
            <v-layout
              v-for="(rule, ith) in filterStylesOnActiveModeByLayerName(
                layer.get('name')
              ).rules"
              :key="ith"
              class="pl-2"
              row
              wrap
              align-center
            >
              <v-flex xs1>
                <v-simple-checkbox
                  style="width: 27px;height: 38px;"
                  :ripple="false"
                  v-if="
                    filterStylesOnActiveModeByLayerName(layer.get('name')).rules
                      .length > 1
                  "
                  :key="layer.get('attributeDisplayStatusKey')"
                  :color="appColor.secondary"
                  :value="isLayerAttributeVisible(layer, ith)"
                  @input="
                    attributeLevelRendering(
                      vectorTileStylesCopy[layer.get('name')].style.rules[ith]
                        .filter[0],
                      layer,
                      ith
                    )
                  "
                >
                </v-simple-checkbox>
              </v-flex>
              <v-flex xs11>
                <span
                  class="justify-start"
                  style="padding-right: 50px"
                  :ref="`legend-vector-${layer.get('name') + ith}`"
                  v-html="renderLegend(layer, ith)"
                >
                </span>
              </v-flex>
            </v-layout>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LegendRenderer from "../../../../utils/LegendRenderer";
import Legend from "../controls/Legend";
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../../../../EventBus";

export default {
  props: ["layer"],
  mixins: [Legend],
  data: () => ({
    legendRerenderOnActiveMode: 0
  }),
  watch: {
    //Rerendering the legend part when calculationModes value changes
    "calculationMode.active": function() {
      this.legendRerenderOnActiveMode += 1;
    }
  },
  methods: {
    isLayerAttributeVisible(layer, ith) {
      //Checkbox will be checked or unchecked based on layer attribute visibility.
      const name = layer.get("name");
      const attributeStyle = this.filterStylesOnActiveModeByLayerName(name)
        .rules[ith].filter[0];
      if (!attributeStyle) {
        return false;
      }
      return true;
    },
    attributeLevelRendering(filter, layer, ith) {
      //Display or hide layer on attribute level.
      const name = layer.get("name");
      const styleFilter = this.filterStylesOnActiveModeByLayerName(name).rules[
        ith
      ];
      if (styleFilter.filter[0]) {
        styleFilter.filter[0] = "";
      } else {
        styleFilter.filter[0] = filter;
      }
      layer.getSource().changed();
      layer.set(
        "attributeDisplayStatusKey",
        layer.get("attributeDisplayStatusKey") + 1
      );
    },
    renderLegend(layer, index) {
      //Render individual legend on attribue level.
      setTimeout(() => {
        const name = layer.get("name");
        const styleObj = this.vectorTileStyles;
        let styleTranslation = this.vectorTileStyles[name].translation;
        const currentLocale = this.$i18n.locale;
        if (styleObj[name] && styleObj[name].format === "geostyler") {
          let el = this.$refs[`legend-vector-${name + index}`];
          el = el ? el : [];
          if (el.length) {
            if (Array.isArray(el) && el.length > 0) {
              el = el[0];
            }
            // Remove existing svg elements on update (Workaround)
            if (el && el.childNodes.length > 0) {
              el.removeChild(el.childNodes[0]);
            }
            const style = this.filterStylesOnActiveModeByLayerName(name);
            let iStyle = style.rules[index];
            const renderer = new LegendRenderer({
              maxColumnWidth: 260,
              overflow: "auto",
              styles: [
                {
                  name: style.name,
                  rules: [iStyle]
                }
              ],
              size: [260, 300],
              translation: { styleTranslation, currentLocale }
            });

            renderer.render(el);
          }
        }
      }, 100);
    },
    getWMSLayerNames(layer) {
      const layerUrl = layer.getSource().getUrl();
      const layerKeyNames = new URL(layerUrl).searchParams.get("LAYERS");
      return layerKeyNames || "";
    }
  },
  created() {
    EventBus.$on("ol-interaction-activated", type => {
      if (type === "languageChange") {
        this.legendRerenderOnActiveMode += 1;
      }
    });
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig",
      calculationMode: "calculationMode"
    }),
    ...mapFields("map", {
      vectorTileStyles: "vectorTileStyles",
      vectorTileStylesCopy: "vectorTileStylesCopy"
    })
  }
};
</script>
