<template>
  <div class="text-center">
    <v-dialog v-model="dialog" scrollable width="650">
      <template v-slot:activator="{ on, attrs }">
        <v-icon v-bind="attrs" small v-on="on">
          fas fa-link
        </v-icon>
      </template>

      <v-card v-if="option === 'first'">
        <v-app-bar :color="appColor.primary" dark>
          <v-app-bar-nav-icon
            ><v-icon>fas fa-layer-group</v-icon></v-app-bar-nav-icon
          >
          <v-toolbar-title>{{
            $t("externalGeoportals.selectGeoportal")
          }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-app-bar-nav-icon @click="$emit('cancelHandlerEmiter')"
            ><v-icon>close</v-icon></v-app-bar-nav-icon
          >
        </v-app-bar>
        <v-card-text style="padding: 20px;">
          <h2 class="mb-4 grey--text text--darken-3">
            {{ translate("builtInGeoportals", "title") }}
          </h2>
          <div>
            <div class="cards">
              <div
                v-for="(geoportal, idx) in geoportals"
                :key="idx"
                class="cardBox"
                @click="builtInDataHandler(geoportal)"
              >
                <div class="overlay">+</div>
                <img :src="geoportal.thumbnail_url" alt="" />
                <div class="content">
                  <p>{{ geoportal.name }}</p>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
        <v-card-text style="padding: 20px; padding-bottom: 20px">
          <h2 class="mb-4 grey--text text--darken-3">
            {{ translate("ownGeoportals", "title") }}
          </h2>
          <v-layout style="padding: 0 12px;" row align-center>
            <v-flex xs10>
              <v-form ref="form" lazy-validation>
                <v-alert type="error" v-if="error">
                  {{ error }}
                </v-alert>
                <v-text-field
                  v-model="url"
                  label="Source Url"
                  required
                ></v-text-field>
              </v-form>
            </v-flex>
            <v-flex xs2 text-right>
              <v-btn
                text
                @click="layerDataHandler"
                :style="`color: ${appColor.primary}`"
                >ADD</v-btn
              >
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
      <v-card v-if="option === 'upload'">
        <v-app-bar :color="appColor.primary" dark>
          <v-app-bar-nav-icon
            ><v-icon>fas fa-layer-group</v-icon></v-app-bar-nav-icon
          >
          <v-toolbar-title>{{
            $t("externalGeoportals.externalGeoportal")
          }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-app-bar-nav-icon @click="cancelHandler"
            ><v-icon>close</v-icon></v-app-bar-nav-icon
          >
        </v-app-bar>
        <vue-scroll>
          <v-card-text class="pa-6">
            <h2
              class="mb-4 grey--text text--darken-3"
              v-if="currentLayerWMSTitle"
            >
              {{ translate("ownGeoportals", "getLayersFrom") }} "{{
                currentLayerWMSTitle
              }}"
            </h2>
            <v-form ref="form" lazy-validation>
              <v-alert type="error" v-if="error">
                {{ error }}
              </v-alert>
              <v-text-field
                v-model="searchByName"
                label="Search by name"
                required
              ></v-text-field>
            </v-form>
            <div>
              <p class="h6">Results</p>
              <v-card
                v-for="(simpleLayer, idx) in searchedListData"
                @mouseover="onHoverHandler(simpleLayer)"
                @mouseleave="onMouseLeaveHandler(simpleLayer)"
                :key="idx"
                class="mx-auto mb-2"
                style="display: flex"
              >
                <v-card-text>
                  <div class="font-weight-bold">{{ simpleLayer.title }}</div>
                  <p class="layerDescription" :ref="`description-${idx}`">
                    {{ simpleLayer.description }}
                  </p>
                  <p
                    @click="expandStyle(idx)"
                    :style="`cursor: pointer; color: ${appColor.primary};`"
                  >
                    {{ translate("ownGeoportals", "seeMore") }}
                  </p>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    text
                    @click="
                      $emit('getLayerInfo', {
                        data: simpleLayer,
                        currentHoveredLayer: previewLayer
                      })
                    "
                    color="deep-purple accent-4"
                  >
                    <v-icon small :color="appColor.primary"
                      >fas fa-circle-plus</v-icon
                    >
                  </v-btn>
                </v-card-actions>
              </v-card>
            </div>
          </v-card-text>
        </vue-scroll>
      </v-card>
      <pre-defined-geoportals
        :preDefinedLayerData="preDefinedGeoportals"
        @cancelHandlerEmiter="cancelHandler"
        @findAllTheLayersInGeoportal="findAllAvailableLayers"
        v-if="option === 'second'"
      ></pre-defined-geoportals>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { Mapable } from "../../../mixins/Mapable";
import TileLayer from "ol/layer/Tile";
import TileWMS from "ol/source/TileWMS";
import PreDefinedGeoportals from "./PreDefinedGeoportals.vue";

export default {
  mixins: [Mapable],
  data: () => ({
    url: "",
    dialog: false,
    error: "",
    option: "first",
    value: 0,
    preDefinedGeoportals: [],
    geoportals: [],
    layerListToAdd: [],
    searchedListData: [],
    searchByName: "",
    previewLayer: null,
    currentLayerWMSTitle: "",
    CurrentPage: 1
  }),
  watch: {
    searchByName(newValue) {
      if (!newValue) {
        this.searchedListData = this.layerListToAdd;
      } else {
        this.searchedListData = this.layerListToAdd.filter(layer =>
          layer.title.toLowerCase().match(newValue.toLowerCase())
        );
      }
    }
  },
  components: {
    "pre-defined-geoportals": PreDefinedGeoportals
  },
  computed: {
    ...mapGetters("app", {
      appConfig: "appConfig",
      appColor: "appColor"
    })
  },
  methods: {
    getAllTheLayers(preDefined) {
      // We will extract the data from geoadmin
      preDefined.forEach(geoportal => {
        this.geoportals.push(geoportal);
      });
    },
    getTheCapabilitiesFromLink(config, layer) {
      if (layer[config["url"]] !== undefined) {
        let finalUrl = "";
        if (layer[config["url"]].includes("?")) {
          finalUrl =
            layer[config["url"]] + "SERVICE=WMS&REQUEST=GetCapabilities";
        } else {
          finalUrl =
            layer[config["url"]] + "?SERVICE=WMS&REQUEST=GetCapabilities";
        }
        layer[config["url"]] = finalUrl;
        let finalGeoportalInfo = {
          title: layer.name,
          img:
            "https://images.unsplash.com/photo-1524661135-423995f22d0b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2074&q=80",
          geoportal_url: layer[config["url"]],
          type: layer[config["type"]]
        };
        this.preDefinedGeoportals.push(finalGeoportalInfo);
      }
    },
    onMapBound() {
      let allGeoportals = this.appConfig.geostores;
      this.getAllTheLayers(allGeoportals);
    },
    onHoverHandler(layerInfo) {
      if (!this.previewLayer) {
        let newLayer = new TileLayer({
          source: new TileWMS({
            url: layerInfo.url,
            params: {
              layers: layerInfo.name
            },
            attribution: layerInfo.title
          }),
          group: "external_layers",
          name: layerInfo.title,
          visible: true,
          opacity: 1,
          type: "wmts"
        });
        this.map.addLayer(newLayer);
        this.previewLayer = newLayer;
      }
    },
    onMouseLeaveHandler(layerInfo) {
      if (this.previewLayer.get("name") === layerInfo.title) {
        this.map.removeLayer(this.previewLayer);
        this.previewLayer = null;
      }
    },
    // navigation through the popup
    changeOption(value) {
      this.option = value;
    },
    cancelHandler() {
      this.url = "";
      this.layerListToAdd = [];
      this.searchedListData = [];
      this.error = "";
      this.dialog = false;
      this.option = "first";
      this.searchByName = "";
    },
    builtInDataHandler(geoportal) {
      this.option = "second";
      if (geoportal.type === "geoadmin") {
        let configuration = geoportal.configuration;

        fetch(geoportal.url)
          .then(result => result.json())
          .then(data => {
            for (let i = 0; i < data.length; i++) {
              this.getTheCapabilitiesFromLink(configuration, data[i]);
            }
          });
      }
      // console.log("getting the command", geoportal);
    },
    layerDataHandler() {
      if (this.url !== "") {
        this.error = "";
        this.layerListToAdd = [];
        const data = {
          layer_url: this.url
        };
        this.findAllAvailableLayers(data);
        // this.dialog = false;
        this.url = "";
      } else {
        this.error = "Make sure to fill all the required fields";
      }
    },
    // this will fetch all the data from the given links if it has capabilities
    findAllAvailableLayers(data) {
      if (
        data.layer_url.toLowerCase().includes("service=wms") &&
        data.layer_url.toLowerCase().includes("request=getcapabilities")
      ) {
        fetch(data.layer_url)
          .then(result => {
            return result.text();
          })
          .then(datares => {
            let parser = new DOMParser(),
              xmlDoc = parser.parseFromString(datares, "text/xml");
            let names = [...xmlDoc.getElementsByTagName("Layer")];
            this.currentLayerWMSTitle = xmlDoc.getElementsByTagName(
              "Title"
            )[0].textContent;
            let type = xmlDoc.getElementsByTagName("Name")[0].textContent;
            names.forEach((layerElement, idx) => {
              if (idx !== 0) {
                let layerPossibility = {
                  title: layerElement.getElementsByTagName("Title")[0]
                    .textContent,
                  name: layerElement.getElementsByTagName("Name")[0]
                    .textContent,
                  url: data.layer_url.split("?")[0] + "?",
                  type: type
                };
                for (const childElem of layerElement.children) {
                  if (childElem.nodeName === "Abstract") {
                    layerPossibility.description = layerElement.getElementsByTagName(
                      "Abstract"
                    )[0].textContent;

                    if (layerElement.getElementsByTagName("LegendURL")[0]) {
                      let layerLegends = layerElement.getElementsByTagName(
                        "LegendURL"
                      );
                      let legendUrlArr = [];
                      for (const layerLegend of layerLegends) {
                        legendUrlArr.push(
                          layerLegend
                            .getElementsByTagName("OnlineResource")[0]
                            .getAttribute("xlink:href")
                        );
                      }
                      layerPossibility.legendUrl = legendUrlArr;
                      this.layerListToAdd.push(layerPossibility);
                      this.searchedListData.push(layerPossibility);
                      return;
                    }

                    this.layerListToAdd.push(layerPossibility);
                    this.searchedListData.push(layerPossibility);
                    return;
                  }
                }
                layerPossibility.description = "No description...";
                this.layerListToAdd.push(layerPossibility);
                this.searchedListData.push(layerPossibility);
              }
            });
            this.option = "upload";
          });
      } else {
        this.error =
          "Make sure to write an available link that contains all the capabilities!";
      }
    },
    expandStyle(id) {
      if (
        this.$refs[`description-${id}`][0].style.maxHeight === "fit-content"
      ) {
        this.$refs[`description-${id}`][0].style.textOverflow = "ellipsis";
        this.$refs[`description-${id}`][0].style.maxHeight = "65px";
      } else {
        this.$refs[`description-${id}`][0].style.textOverflow = "clip";
        this.$refs[`description-${id}`][0].style.maxHeight = "fit-content";
      }
    },
    translate(type, key) {
      const canTranslate = this.$te(`externalGeoportals.${type}.${key}`);
      if (canTranslate) {
        return this.$t(`externalGeoportals.${type}.${key}`);
      } else {
        return key;
      }
    }
  }
};
</script>

<style scoped>
.button-categorizer {
  width: 100%;
  margin-top: 20px;
}

.cards {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr;
  grid-row-gap: 20px;
  justify-items: center;
  margin-top: 20px;
}

.cardBox {
  width: 90px;
  height: 120px;
  cursor: pointer;
  position: relative;
  box-shadow: rgba(0, 0, 0, 0.05) 0px 0px 0px 1px;
}

.cardBox img {
  width: 100%;
  height: 70%;
  object-fit: cover;
}

.cardBox .content {
  width: 100%;
  height: 30%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 5px;
  text-align: center;
}
.cardBox .content p {
  font-size: 10px;
  font-weight: 400;
  line-height: 10px;
}

.overlay {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 70%;
  background: rgba(0, 0, 0, 0.474);
  display: flex;
  justify-content: center;
  align-items: center;
  color: rgb(188, 188, 188);
  font-weight: bolder;
  font-size: 45px;
  transition: all 0.3s ease-in-out;
  opacity: 0;
}

.cardBox:hover .overlay {
  opacity: 0.7;
  color: white;
}

.layerDescription {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 65px;
  font-size: 12px;
}
</style>
