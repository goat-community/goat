<template>
  <v-dialog v-model="show" scrollable max-width="350px">
    <v-card>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon><v-icon>info</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{
          $t("isochrones.results.showAdditionalData")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>

      <v-card-text class="mt-4 mb-0" primary-title>
        <div>
          <v-checkbox
            :color="appColor.secondary"
            :label="`Isochrone Network`"
            :input-value="
              calculation.additionalData && calculation.additionalData.network
                ? calculation.additionalData.network.state
                : false
            "
            @change="toggleIsochroneAdditionalData('network')"
            hide-details
          ></v-checkbox>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import { mapGetters } from "vuex";
export default {
  mixins: [Mapable],
  props: ["calculation", "visible"],
  computed: {
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    },
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig"
    })
  },
  methods: {
    toggleIsochroneAdditionalData(type) {
      if (!this.calculation.additionalData) {
        this.calculation.additionalData = {};
      }
      if (!this.calculation.additionalData[type]) {
        this.calculation.additionalData[type] = {
          state: true
        };
      } else {
        this.calculation.additionalData[type].state = !this.calculation
          .additionalData[type].state;
      }
      this.$emit("toggleIsochroneAdditionalData", type);
      this.$emit("close");
    }
  }
};
</script>

<style scoped>
.v-card__text,
.v-card__title {
  word-break: normal !important;
}
</style>
