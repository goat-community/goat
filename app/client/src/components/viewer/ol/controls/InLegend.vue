<template>
  <div>
    <span style="display: none">{{ layerName }}</span>
    <div v-if="item.mapLayer.get('legendGraphicUrl')">
      <img
        crossorigin="anonymous"
        style="max-width: 100%; padding-left: 50px"
        :src="item.mapLayer.get('legendGraphicUrl')"
        class="white--text mt-0 pt-0"
      />
    </div>
    <div v-else>
      <div v-if="item.mapLayer.get('type') === 'WMS'">
        <template
          v-for="(layerName, index2) in item.mapLayer
            .getSource()
            .getParams()
            .LAYERS.split(',')"
        >
          <div :key="index2">
            <img
              crossorigin="anonymous"
              style="max-width: 100%; padding-left: 50px"
              :src="getWMSLegendImageUrl(item.mapLayer, layerName)"
              class="white--text mt-0 pt-0"
            />
            <br />
          </div>
        </template>
      </div>
      <div :key="legendRerenderOnActiveMode">
        <div
          v-if="
            ['VECTORTILE', 'VECTOR'].includes(item.mapLayer.get('type')) &&
              $appConfig.stylesObjCopy[item.mapLayer.get('name')]
          "
          style="text-align: center; padding: 20px"
          :key="item.layerTreeKey"
        >
          <div v-if="$appConfig.stylesObjCopy[item.mapLayer.get('name')]">
            <v-layout
              v-for="(rule, ith) in filterStylesOnActiveModeByLayerName(
                item.mapLayer.get('name')
              ).rules"
              :key="ith"
              class="pl-2"
              row
              wrap
              align-center
            >
              <v-flex xs1>
                <v-simple-checkbox
                  :ripple="false"
                  style="width: 27px; height: 38px"
                  :color="activeColor.primary"
                  v-if="
                    filterStylesOnActiveModeByLayerName(
                      item.mapLayer.get('name')
                    ).rules.length > 1
                  "
                  :key="item.attributeDisplayStatusKey"
                  :value="isLayerAttributeVisible(item, ith)"
                  @input="
                    attributeLevelRendering(
                      $appConfig.stylesObjCopy[item.mapLayer.get('name')].style
                        .rules[ith].filter[0],
                      item,
                      ith
                    )
                  "
                >
                </v-simple-checkbox>
              </v-flex>
              <v-flex xs11>
                <span
                  @click="openStyleDialog(item, ith)"
                  class="justify-start"
                  style="padding-right: 50px; cursor: pointer"
                  :ref="`legend-vector-${item.name + ith}`"
                  v-html="renderLegend(item, ith)"
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

export default {
  props: ["item", "openStyleDialog", "layerName"],
  mixins: [Legend],
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    })
  },
  data: () => ({
    legendRerenderOnActiveMode: 0
  }),
  watch: {
    //Rerendering the legend part when calculationModes value changes
    "calculationOptions.calculationModes.active": function() {
      this.legendRerenderOnActiveMode += 1;
    }
  },
  methods: {
    isLayerAttributeVisible(item, ith) {
      //Checkbox will be checked or unchecked based on layer attribute visibility.
      const name = item.mapLayer.get("name");
      const attributeStyle = this.filterStylesOnActiveModeByLayerName(name)
        .rules[ith].filter[0];
      if (!attributeStyle) {
        return false;
      }
      return true;
    },
    attributeLevelRendering(filter, item, ith) {
      //Display or hide layer on attribute level.
      const name = item.mapLayer.get("name");
      const styleFilter = this.filterStylesOnActiveModeByLayerName(name).rules[
        ith
      ];
      if (styleFilter.filter[0]) {
        styleFilter.filter[0] = "";
      } else {
        styleFilter.filter[0] = filter;
      }
      item.mapLayer.getSource().changed();
      this.item.attributeDisplayStatusKey += 1;
    },
    renderLegend(item, index) {
      //Render individual legend on attribue level.
      setTimeout(() => {
        item = item.mapLayer;
        const styleObj = this.$appConfig.stylesObj;
        const name = item.get("name");
        let styleTranslation = this.$appConfig.stylesObj[name].translation;
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
              maxColumnWidth: 240,
              overflow: "auto",
              styles: [
                {
                  name: style.name,
                  rules: [iStyle]
                }
              ],
              size: [230, 300],
              translation: { styleTranslation, currentLocale }
            });
            renderer.render(el);
          }
        }
      }, 100);
    }
  }
};
</script>
