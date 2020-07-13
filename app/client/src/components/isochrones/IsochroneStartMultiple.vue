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
        :disabled="isBusy"
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
      <!-- STOP CALC -->
      <v-card-actions v-if="isBusy">
        <v-spacer></v-spacer>
        <v-tooltip v-if="isBusy" top>
          <template v-if="isBusy" v-slot:activator="{ on }">
            <v-btn
              v-show="isBusy"
              v-on="on"
              small
              @click.stop="stopIsochroneCalc"
              class="white--text"
              color="error"
            >
              <v-icon color="white">close</v-icon>{{ $t("buttonLabels.stop") }}
            </v-btn>
          </template>
          <span>{{ $t("isochrones.stopIsochroneCalc") }}</span>
        </v-tooltip>
      </v-card-actions>

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
            :loading="isBusy"
            @click="calcuateBtn"
          >
            {{ $t("isochrones.multiple.calculate") }}
          </v-btn>
        </v-card-actions>
      </template>
    </v-flex>
    <v-progress-linear
      v-if="isBusy"
      indeterminate
      height="1"
      class="mx-0 pb-0"
      color="green"
    ></v-progress-linear>
  </v-flex>
</template>
<script>
//Store imports
import { mapGetters, mapActions } from "vuex";
import { mapFields } from "vuex-map-fields";

import { EventBus } from "../../EventBus";
import { Mapable } from "../../mixins/Mapable";
import { KeyShortcuts } from "../../mixins/KeyShortcuts";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";
import { unByKey } from "ol/Observable";

import OlMultiIsochroneController from "../../controllers/OlMultiIsochroneController";

export default {
  mixins: [Mapable, InteractionsToggle, KeyShortcuts],
  data: () => ({
    isIsochroneStartElVisible: true,
    interactionType: "isochrone-multiple-interaction"
  }),
  computed: {
    ...mapGetters("isochrones", {
      multiIsochroneCalculationMethods: "multiIsochroneCalculationMethods",
      countPois: "countPois",
      isBusy: "isBusy",
      cancelReq: "cancelReq"
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
      me.olIsochroneCtrl = new OlMultiIsochroneController(me.map);
      me.olIsochroneCtrl.createSelectionLayer();
    },
    toggleInteraction() {
      const me = this;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", me.interactionType);
      me.olIsochroneCtrl.removeInteraction();
      me.olIsochroneCtrl.addInteraction("multiple");
      me.map.getTarget().style.cursor = "pointer";
      if (this.addKeyupListener) {
        this.addKeyupListener();
      }
    },
    calcuateBtn() {
      this.calculateIsochrone();
      this.clear();
    },
    stopIsochroneCalc() {
      if (this.cancelReq instanceof Function) {
        this.cancelReq("cancelled");
      }
    },
    clear() {
      if (this.olIsochroneCtrl.mapClickListenerKey) {
        unByKey(this.olIsochroneCtrl.mapClickListenerKey);
      }
      this.map.getTarget().style.cursor = "";
      this.activeMultiIsochroneMethod = null;
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
    },
    /**
     * stops multi isochrone interaction
     */
    stop() {
      const me = this;
      me.clear();
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
