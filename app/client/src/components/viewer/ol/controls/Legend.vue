<template>
  <v-expansion-panels
    class="elevation-3"
    dark
    style="position:absolute;bottom:35px;right:10px;maxWidth: 200px;"
  >
    <v-expansion-panel style="background-color: white;">
      <v-expansion-panel-header
        >{{ $t("map.layerLegend.title") }}
        <template v-slot:actions>
          <v-icon small>$vuetify.icons.expand</v-icon>
        </template>
      </v-expansion-panel-header>
      <v-expansion-panel-content style="max-height:400px;">
        <vue-scroll>
          <template v-for="(item, index) in layers">
            <div
              :key="index"
              v-if="item.getVisible() === true"
              style="padding-right:10px;"
            >
              <p class="grey--text text--darken-2 pb-0 mb-1 mt-2 subtitle-2">
                {{
                  $te(`map.layerName.${item.get("name")}`)
                    ? $t(`map.layerName.${item.get("name")}`)
                    : item.get("name")
                }}
              </p>
              <v-divider></v-divider>
              <!-- Parent layer can have multiple child layers, so we need to loop through -->
              <template
                v-for="(layerName, index2) in item
                  .getSource()
                  .getParams()
                  .LAYERS.split(',')"
              >
                <div :key="index2">
                  <img
                    style="max-width: 100%;"
                    :src="getWMSLegendImageUrl(item, layerName)"
                    class="white--text mt-0 pt-0"
                  />
                  <br />
                </div>
              </template>
            </div>
          </template>
        </vue-scroll>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<script>
import { Mapable } from "../../../../mixins/Mapable";
import { getAllChildLayers, getWMSLegendURL } from "../../../../utils/Layer";
export default {
  mixins: [Mapable],
  name: "map-legend",
  data: () => ({
    layers: []
  }),
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;
      const allLayers = getAllChildLayers(me.map);
      me.layers = allLayers.filter(
        layer =>
          layer.getSource().serverType_ === "geoserver" &&
          layer.get("displayInLegend") !== false
      );
    },
    getWMSLegendImageUrl(item, layerName) {
      let layerUrl = item.getSource().getUrl();
      if (layerUrl.startsWith("/")) {
        layerUrl = window.location.origin + layerUrl;
      }
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
        this.$i18n.locale
      );
      return legedUrl;
    }
  }
};
</script>
<style lang="css" scoped>
.v-expansion-panel-header {
  min-height: 30px;
  padding: 5px;
  background-color: #4caf50;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 2px 0px 0px 5px;
}
</style>
