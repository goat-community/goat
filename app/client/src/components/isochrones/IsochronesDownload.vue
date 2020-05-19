<template>
  <v-dialog v-model="show" scrollable max-width="350px">
    <v-card>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-file-download</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>{{ $t("isochrones.download.title") }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <v-card-title primary-title>
          <v-flex xs12>
            <v-text-field
              :label="$t(`isochrones.download.fileName`)"
              v-model="name"
              type="text"
            ></v-text-field>
            <v-select
              :items="items"
              v-model="selected"
              :label="$t(`isochrones.download.outputFormat`)"
            ></v-select>
          </v-flex>
        </v-card-title>
      </vue-scroll>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" @click="download()" color="green"
          ><v-icon left>fas fa-download</v-icon
          >{{ $t("isochrones.download.download") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { featuresToGeojson } from "../../utils/MapUtils";
import { saveAs } from "file-saver";
import http from "../../services/http";

export default {
  props: {
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  data: () => ({
    name: "isochrones-export",
    selected: "GeoJson",
    items: ["GeoJson", "Shapefile"]
  }),
  methods: {
    download() {
      let me = this;
      let exportName = me.name;
      if (me.name.length === 0) {
        exportName = "export";
      }
      if (me.selected === "GeoJson") {
        let featuresArray = [];
        let data = me.calculation.data;
        data.forEach(isochrone => {
          let id = isochrone.id;
          let feature = me.isochroneLayer.getSource().getFeatureById(id);
          if (feature) {
            let clonedFeature = feature.clone();
            clonedFeature.unset("isVisible");
            featuresArray.push(clonedFeature);
          }
        });
        let json = featuresToGeojson(featuresArray, "EPSG:3857");
        let blob = new Blob([json], { type: "application/json" });

        saveAs(blob, `${exportName}.json`);
      } else if (me.selected === "Shapefile") {
        const objectId = me.calculation.data[0].objectId;
        http
          .get("./geoserver/wfs", {
            params: {
              service: "WFS",
              version: " 1.1.0",
              request: "GetFeature",
              viewparams: `objectid:${objectId}`,
              outputFormat: "shape-zip",
              typeNames: "cite:download_isochrones",
              srsname: "EPSG:4326"
            },
            responseType: "blob"
          })
          .then(response => {
            saveAs(response.data, `${exportName}.zip`);
          });
      }
    }
  },
  computed: {
    ...mapGetters("isochrones", { isochroneLayer: "isochroneLayer" }),
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    }
  }
};
</script>
