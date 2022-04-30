<template>
  <div class="mt-4">
    <v-tooltip v-if="!isVisible" right>
      <template v-slot:activator="{ on }">
        <v-btn
          v-if="!isVisible"
          class="search-button"
          v-on="on"
          fab
          dark
          x-small
          @click="isVisible = !isVisible"
          :color="color"
        >
          <v-icon medium>fas fa-search</v-icon>
        </v-btn>
      </template>
      <span>{{ $t("map.tooltips.search") }}</span>
    </v-tooltip>
    <v-autocomplete
      v-if="isVisible"
      solo
      rounded
      style="z-index: 3;width:300px;"
      v-model="model"
      :items="items"
      :loading="isLoading"
      :label="$t('map.tooltips.search')"
      :search-input.sync="search"
      item-text="display_name"
      append-icon=""
      clear-icon="close"
      @click:clear="clearSearch"
      @change="zoomToLocation"
      autofocus
      clearable
      item-value="osm_id"
      hide-details
      hide-no-data
      no-filter
      prepend-inner-icon="search"
      return-object
      class="elevation-4"
      :menu-props="{ maxHeight: 400 }"
    >
      <template slot="append">
        <v-icon v-show="!search" v-on:click.stop.prevent="closeSearch" left
          >chevron_left</v-icon
        >
      </template>
      <template v-slot:item="data">
        <template v-if="typeof data.item !== 'object'">
          <v-list-item-content v-text="data.item"></v-list-item-content>
        </template>
        <template v-else>
          <template v-if="data.item.icon">
            <img :src="data.item.icon" class="mr-3" />
          </template>
          <v-list-item-content style="z-index: 1;width:220px;">
            <v-list-item-title
              v-html="data.item.display_name"
            ></v-list-item-title>
            <v-list-item-subtitle
              v-if="data.item.subtitle"
              v-html="data.item.subtitle"
            ></v-list-item-subtitle>
          </v-list-item-content>
        </template>
      </template>
      <template slot="append-item"
        ><div class="nominatim-attribution pa-1 mt-2">
          <a href="http://www.openstreetmap.org/copyright" target="new"
            >© OpenStreetMap contributors</a
          >
        </div>
      </template>
    </v-autocomplete>
  </div>
</template>
<script>
import axios from "axios";
import { debounce } from "../../../../utils/Helpers";
import { geojsonToFeature } from "../../../../utils/MapUtils";
import { fromLonLat } from "ol/proj";
import { boundingExtent } from "ol/extent";
import { getSearchHighlightStyle } from "../../../../style/OlStyleDefs";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";

export default {
  props: {
    map: { type: Object, required: true },
    color: { type: String },
    viewbox: { type: Array, required: false }
  },
  data() {
    return {
      isVisible: false,
      descriptionLimit: 30,
      entries: [],
      model: null,
      search: null,
      isLoading: false,
      highlightLayer: null
    };
  },
  name: "search",
  methods: {
    zoomToLocation() {
      if (!this.search || !this.model) return;
      const x1 = parseFloat(this.model.boundingbox[2]);
      const y1 = parseFloat(this.model.boundingbox[0]);
      const x2 = parseFloat(this.model.boundingbox[3]);
      const y2 = parseFloat(this.model.boundingbox[1]);
      const extent = boundingExtent([
        fromLonLat([x1, y1]),
        fromLonLat([x2, y2])
      ]);
      const feature = new Feature(
        new Point(
          fromLonLat([parseFloat(this.model.lon), parseFloat(this.model.lat)])
        )
      );
      this.highlightLayer.getSource().clear();
      this.highlightLayer.getSource().addFeature(feature);
      if (this.model.geojson) {
        const olFeatures = geojsonToFeature(this.model.geojson, {
          dataProjection: "EPSG:4326",
          featureProjection: "EPSG:3857"
        });
        this.highlightLayer.getSource().addFeatures(olFeatures);
      }
      this.map.getView().fit(extent, {
        nearest: true,
        duration: 1000,
        maxZoom: 19,
        callback: () => {
          this.map.render();
        }
      });
    },
    clearSearch() {
      this.entries = [];
      this.count = 0;
      this.highlightLayer.getSource().clear();
    },
    closeSearch() {
      this.clearSearch();
      this.isVisible = false;
    }
  },
  computed: {
    items() {
      return this.entries.map(entry => {
        const subtitle = [];
        if (entry.class) subtitle.push(entry.class);
        if (entry.type) subtitle.push(entry.type);
        return Object.assign({}, entry, {
          subtitle: subtitle.join(" - ")
        });
      });
    }
  },
  watch: {
    search: debounce(function() {
      if (!this.search) {
        this.clearSearch();
        return;
      }
      // Items have already been requested
      if (this.isLoading) return;
      this.isLoading = true;
      let url = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q=${this.search}&polygon_geojson=0&limit=10`;
      if (this.viewbox.length === 4) {
        url += `&viewbox=${this.viewbox.toString()}&bounded=1`;
      }
      axios
        .get(url)
        .then(response => {
          this.count = response.data.length;
          this.entries = response.data;
          this.isLoading = false;
        })
        .catch(() => {
          this.isLoading = false;
        });
    }, 500)
  },
  created() {
    this.highlightLayer = new VectorLayer({
      zIndex: 100,
      source: new VectorSource(),
      style: getSearchHighlightStyle
    });
    this.map.addLayer(this.highlightLayer);
  }
};
</script>
<style lang="scss">
.search-button {
  z-index: 1;
}
.v-autocomplete__content.v-menu__content {
  transform-origin: center top !important;
  transform: scale(0.9) !important;
}
.v-autocomplete__content {
  z-index: 1001 !important;
}
.nominatim-attribution {
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
}

.nominatim-attribution a {
  color: #fff !important;
  text-decoration: none !important;
}
.v-autocomplete__content > div {
  padding-bottom: 0px !important;
}
</style>
