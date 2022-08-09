<template>
  <v-card>
    <v-app-bar :color="appColor.primary" dark>
      <v-app-bar-nav-icon @click="$emit('goBack')">
        <v-icon>fas fa-chevron-left</v-icon>
      </v-app-bar-nav-icon>
      <v-app-bar-nav-icon>
        <v-icon>fas fa-layer-group</v-icon>
      </v-app-bar-nav-icon>
      <v-toolbar-title>{{
        $t("externalGeoportals.selectGeoportal")
      }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-app-bar-nav-icon @click="$emit('cancelHandlerEmiter')">
        <v-icon>close</v-icon>
      </v-app-bar-nav-icon>
    </v-app-bar>
    <vue-scroll>
      <v-card-text class="pa-6">
        <h2 class="mb-4 grey--text text--darken-3">
          {{ translate("builtInGeoportals", "title") }}
        </h2>
        <v-text-field
          v-model="searchByName"
          label="Search by name"
          required
        ></v-text-field>
        <div>
          <div class="cards">
            <v-tooltip
              top
              v-for="(layer, idx) in filteredGeoportalByPage"
              :key="idx"
            >
              <template v-slot:activator="{ on, attrs }">
                <div
                  class="cardBox"
                  @click="creatingALayerObject(layer)"
                  v-bind="attrs"
                  v-on="on"
                >
                  <div class="overlay">+</div>
                  <img :src="layer.img" alt="" />
                  <div class="content">
                    <p>{{ layer.title }}</p>
                  </div>
                </div>
              </template>
              <span>{{ layer.title }}</span>
            </v-tooltip>
          </div>
        </div>
        <div class="text-center mt-5">
          <v-pagination
            v-model="CurrentPage"
            :color="appColor.primary"
            :length="Math.round(searchedListData.length / 15)"
            circle
          ></v-pagination>
        </div>
      </v-card-text>
    </vue-scroll>
    <v-dialog v-model="showErrPopup" persistent width="300">
      <v-card>
        <v-app-bar :color="appColor.primary" dark>
          <v-app-bar-nav-icon
            ><v-icon>fas fa-circle-info</v-icon></v-app-bar-nav-icon
          >
          <v-toolbar-title>Info</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-text class="pt-3">
          {{ $t("externalGeoportals.popups.info") }}
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            :color="appColor.primary"
            text
            @click="$emit('changeErrPopup')"
          >
            {{ $t("externalGeoportals.popups.agreement") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: ["preDefinedLayerData", "showErrPopup"],
  data: () => ({
    CurrentPage: 1,
    searchByName: "",
    searchedListData: []
    // LayerNotLoading: false
  }),
  watch: {
    searchByName(newValue) {
      if (!newValue) {
        this.searchedListData = this.preDefinedLayerData;
      } else {
        this.searchedListData = this.preDefinedLayerData.filter(layer =>
          layer.title.toLowerCase().match(newValue.toLowerCase())
        );
      }
    }
  },
  mounted() {
    this.searchedListData = this.preDefinedLayerData;
    // The only way to remove a display bug, .__vue cannot be accessed since it is created by vutify and I had to select it via javascript for now
    document.querySelector(".__view").style.width = "100px";
  },
  computed: {
    ...mapGetters("app", {
      appConfig: "appConfig",
      appColor: "appColor"
    }),
    filteredGeoportalByPage() {
      return this.searchedListData.filter(
        (layer, idx) =>
          (this.CurrentPage - 1) * 15 < idx && idx < this.CurrentPage * 15 + 1
      );
    }
  },
  methods: {
    translate(type, key) {
      const canTranslate = this.$te(`externalGeoportals.${type}.${key}`);
      if (canTranslate) {
        return this.$t(`externalGeoportals.${type}.${key}`);
      } else {
        return key;
      }
    },
    creatingALayerObject(layer) {
      let newDataLayers = {
        layer_url: layer.geoportal_url
      };

      this.$emit("findAllTheLayersInGeoportal", newDataLayers);
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
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
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
  max-height: 30px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  overflow: hidden;
  text-overflow: ellipsis;
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
