<template>
  <v-card>
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
            v-for="(layer, idx) in filteredGeoportalByPage"
            :key="idx"
            class="cardBox"
            @click="builtInDataHandler(layer)"
          >
            <div class="overlay">+</div>
            <img :src="layer.img" alt="" />
            <div class="content">
              <p>{{ layer.title }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="text-center">
        <v-pagination
          v-model="CurrentPage"
          :length="Math.round(preDefinedLayerData.length / 12)"
          circle
        ></v-pagination>
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
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: ["preDefinedLayerData"],
  data: () => ({
    CurrentPage: 1
  }),
  computed: {
    ...mapGetters("app", {
      appConfig: "appConfig",
      appColor: "appColor"
    }),
    filteredGeoportalByPage() {
      return this.preDefinedLayerData.filter(
        (layer, idx) =>
          (this.CurrentPage - 1) * 12 < idx && idx < this.CurrentPage * 12 + 1
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
    }
  }
};
</script>

<style></style>
