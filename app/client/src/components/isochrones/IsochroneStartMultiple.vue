<template>
  <v-flex xs12>
    <v-card-text class="pr-16 pl-16 pt-0 pb-0">
      <v-divider></v-divider>
    </v-card-text>
    <v-subheader
      @click="isIsochroneStartElVisible = !isIsochroneStartElVisible"
      class="clickable"
    >
      <v-icon
        :class="{
          activeIcon: isIsochroneStartElVisible,
          'mr-3': true
        }"
        style="margin-right: 2px;"
        small
        >fas fa-map-marker-alt</v-icon
      >
      <h3>{{ $t("isochrones.multiple.title") }}</h3>
    </v-subheader>
    <v-flex
      xs12
      v-show="isIsochroneStartElVisible"
      style="overflow: hidden;"
      class="mx-4"
    >
      <v-select
        item-value="value"
        class="select-method-height mx-1 my-1"
        v-model="activeMultiIsochroneMethod"
        :items="multiIsochroneCalculationMethods.values"
        @change="toggleInteraction"
        :label="$t('isochrones.multiple.selectMethod')"
        solo
      >
        <template slot="selection" slot-scope="{ item }">
          {{ $t(`isochrones.multiple.${item.name}`) }}
        </template>
        <template slot="item" slot-scope="{ item }">
          {{ $t(`isochrones.multiple.${item.name}`) }}
        </template>
      </v-select>
      <template v-if="this.activeMultiIsochroneMethod !== null">
        <v-alert
          border="left"
          colored-border
          class="mb-0 mt-2 mx-1 elevation-2"
          icon="info"
          color="green"
          dense
        >
          <span v-html="getInfoLabelText"></span>
        </v-alert>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn outlined class="white--text" color="red" @click="clear">
            {{ $t("isochrones.multiple.clear") }}
          </v-btn>
          <v-btn
            :disabled="isCalculationDisabled"
            outlined
            class="white--text mr-1"
            color="green"
            @click="calculateIsochrone"
          >
            {{ $t("isochrones.multiple.calculate") }}
          </v-btn>
        </v-card-actions>
      </template>
    </v-flex>
  </v-flex>
</template>
<script>
//Store imports
import { mapGetters, mapActions } from "vuex";
import { mapFields } from "vuex-map-fields";

import { EventBus } from "../../EventBus";
import { Mapable } from "../../mixins/Mapable";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";

import OlIsochroneController from "../../controllers/OlIsochroneController";

export default {
  mixins: [Mapable, InteractionsToggle],
  data: () => ({
    isIsochroneStartElVisible: true,
    interactionType: "isochrone-multiple-interaction"
  }),
  computed: {
    ...mapGetters("isochrones", {
      multiIsochroneCalculationMethods: "multiIsochroneCalculationMethods",
      countPois: "countPois"
    }),
    ...mapFields("isochrones", {
      activeMultiIsochroneMethod: "multiIsochroneCalculationMethods.active"
    }),

    isCalculationDisabled() {
      if (this.countPois > 0 && this.countPois < 150) {
        return false;
      } else {
        return true;
      }
    },
    getInfoLabelText() {
      let text = "";
      if (
        this.countPois === 0 &&
        this.activeMultiIsochroneMethod === "study_area"
      ) {
        text = this.$t("isochrones.multiple.studyAreaInfoLabel");
      } else if (
        this.countPois === 0 &&
        this.activeMultiIsochroneMethod === "draw"
      ) {
        text = this.$t("isochrones.multiple.drawBoundaryInfoLabel");
      } else {
        text = `${this.$t("isochrones.multiple.amenityCount")}: ${
          this.countPois
        } (${this.$t("isochrones.multiple.limit")}: 150)`;
      }
      return text;
    }
  },
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    ...mapActions("isochrones", { calculateIsochrone: "calculateIsochrone" }),
    onMapBound() {
      const me = this;
      //Initialize ol isochrone controllers.
      me.olIsochroneCtrl = new OlIsochroneController(me.map);
      me.olIsochroneCtrl.createSelectionLayer();
    },
    toggleInteraction() {
      const me = this;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", me.interactionType);
      me.olIsochroneCtrl.removeInteraction();
      me.olIsochroneCtrl.addInteraction("multiple");
    },
    clear() {
      this.activeMultiIsochroneMethod = null;
    },
    /**
     * stops multi isochrone interaction
     */
    stop() {
      const me = this;
      me.clear();
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
    }
  },
  watch: {
    activeMultiIsochroneMethod: function(val) {
      if (val === null) {
        this.olIsochroneCtrl.clear();
      }
    }
  },
  beforeDestroy() {
    this.activeMultiIsochroneMethod = null;
    this.olIsochroneCtrl.clear();
  }
};
</script>
<style lang="css" scoped>
.activeIcon {
  color: #30c2ff;
}
.select-method-height >>> .v-input__control {
  height: 56px;
}
</style>
