<template>
  <div id="app-tools">
    <!-- App Bar Container -->
    <v-navigation-drawer
      id="app-toolbar-content"
      v-model="container"
      app
      persistent
      stateless
      value="true"
      right
      :permanent="container === true"
      width="350"
      hide-overlay
      class="white left-shadow"
    >
      <vue-scroll>
        <v-layout
          justify-space-between
          column
          fill-height
          style="overflow-y: auto;padding-right:5px;"
        >
          <keep-alive>
            <component v-bind:is="activeUpComponent"></component>
          </keep-alive>
          <v-icon @click="hide" class="close-icon">close</v-icon>
        </v-layout>
      </vue-scroll>
    </v-navigation-drawer>
    <!-- App Bar -->
    <v-navigation-drawer
      id="app-toolbar"
      value="true"
      app
      dark
      persistent
      permanent
      right
      hide-overlay
      :color="activeColor.primary"
      :class="{ 'left-shadow': container === false }"
      width="50"
    >
      <v-layout justify-space-between column fill-height>
        <v-list>
          <template v-for="(item, index) in upItems">
            <v-tooltip left :key="index">
              <template v-slot:activator="{ on }">
                <v-list-item
                  @click="toggleComponent(item.componentToShow)"
                  v-on="on"
                  v-show="
                    !(osmMode === true && item.componentToShow !== 'map-filter')
                  "
                  active-class="red--text"
                  :style="[
                    activeUpComponent === item.componentToShow
                      ? { backgroundColor: activeColor.secondary }
                      : { backgroundColor: activeColor.primary }
                  ]"
                >
                  <v-list-item-action>
                    <v-icon
                      style="color: white;"
                      light
                      v-html="item.icon"
                    ></v-icon>
                  </v-list-item-action>

                  <v-list-item-content>
                    <v-list-item-title v-html="item.text"></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </template>
              <span>{{ item.text }}</span>
            </v-tooltip>
          </template>
        </v-list>
        <v-list justify-end>
          <!-- CHANGE LANGUAGE -->
          <language></language>

          <!-- OSM MAP MODE -->
          <v-tooltip left>
            <template v-slot:activator="{ on }">
              <v-list-item
                v-on="on"
                style="padding: 0 8px;"
                @click="toggleOsmMapMode()"
                :style="
                  osmMode === true
                    ? `background-color: ${activeColor.secondary};`
                    : `background-color: ${activeColor.primary};`
                "
                class="mb-1"
              >
                <v-list-item-action style="min-width:35px;">
                  <v-img
                    :src="require(`../../assets/img/others/osm_icon.png`)"
                    height="35"
                    class="white--text"
                  ></v-img>
                </v-list-item-action>
                <v-list-item-content>
                  <v-list-item-title></v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
            <span>{{ $t("appBar.buttons.osmMapMode") }}</span>
          </v-tooltip>

          <!-- HOMEPAGE LINK -->
          <v-tooltip left>
            <template v-slot:activator="{ on }">
              <v-btn
                dark
                small
                href="http://open-accessibility.org"
                target="_blank"
                class="elevation-0 ma-0 py-1"
                v-on="on"
                :color="activeColor.primary"
              >
                <v-icon color="white" large light>home</v-icon>
              </v-btn>
            </template>

            <span>{{ $t("appBar.buttons.info") }}</span>
          </v-tooltip>
        </v-list>
      </v-layout>
    </v-navigation-drawer>
    <confirm ref="confirm"></confirm>

    <!-- <component
      :visible="showDialog"
      @close="showDialog = false"
      v-bind:is="activeBottomComponent"
    ></component> -->
    <!-- <app-about :visible="showDialog" @close="showDialog = false" /> -->
  </div>
</template>

<script>
// Utilities
import {} from "vuex";

import Settings from "./Settings";
import About from "./About";

import Print from "../print/Print";
import DrawAndMeasure from "../drawAndMeasure/DrawAndMeasure";
import Filter from "../layers/filter/Filter";
import Edit from "../layers/edit/Edit";
import Language from "./Language";
import { mapMutations, mapGetters } from "vuex";
import { EventBus } from "../../EventBus";
import { mapFields } from "vuex-map-fields";

export default {
  name: "app-sidebar",
  components: {
    "map-print": Print,
    "map-draw-measure": DrawAndMeasure,
    "map-filter": Filter,
    "map-edit": Edit,
    "app-settings": Settings,
    "app-about": About,
    language: Language
  },
  data: () => ({
    container: false,
    activeUpComponent: "",
    activeBottomComponent: "",
    responsive: false,
    showDialog: false
  }),
  computed: {
    upItems() {
      return [
        {
          icon: "fas fa-filter",
          text: this.$t("appBar.buttons.filter"),
          componentToShow: "map-filter"
        },
        {
          icon: "fas fa-edit",
          text: this.$t("appBar.buttons.edit"),
          componentToShow: "map-edit"
        },
        {
          icon: "fas fa-print",
          text: this.$t("appBar.buttons.print"),
          componentToShow: "map-print"
        },
        {
          icon: "fas fa-paint-brush",
          text: this.$t("appBar.buttons.drawAndMeasure"),
          componentToShow: "map-draw-measure"
        }
      ];
    },
    bottomItems() {
      return [];
    },
    ...mapGetters("map", {
      osmMode: "osmMode"
    }),
    ...mapFields("app", {
      activeColor: "activeColor"
    })
  },
  methods: {
    toggleComponent(component) {
      if (component === this.activeUpComponent) {
        this.hide();
      } else {
        this.container = true;
        this.activeUpComponent = component;
      }
    },
    toggleDialog(component) {
      this.activeBottomComponent = component;
      this.showDialog = true;
    },
    toggleOsmMapMode() {
      this.hide();
      this.setOsmMode();
      if (this.osmMode === true) {
        // Stop other interactions.
        EventBus.$emit("ol-interaction-activated", "osm-map-mode");
        EventBus.$emit("ol-interaction-stoped", "osm-map-mode");
        this.toggleComponent("map-filter");
        this.activeColor = this.$appConfig.osmMappingColor;
        this.$refs.confirm.open(
          this.$t("map.osmMode.dialogMessage.title"),
          this.$t("map.osmMode.dialogMessage.body"),
          {
            color: this.activeColor.primary,
            icon: "info",
            width: 420,
            showNo: false,
            yesText: this.$t("buttonLabels.ok")
          }
        );
      } else {
        this.activeColor = this.$appConfig.baseColor;
      }
    },
    hide() {
      this.container = false;
      this.activeUpComponent = "";
      this.activeBottomComponent = "";
      this.showDialog = false;
    },
    ...mapMutations("map", {
      setOsmMode: "SET_OSM_MODE"
    })
  }
};
</script>

<style lang="scss">
.activeIcon {
  color: #30c2ff;
}

#app-toolbar {
  .v-list__tile {
    border-radius: 4px;
    &--buy {
      margin-top: auto;
      margin-bottom: 17px;
    }
  }
  .v-image__image--contain {
    top: 9px;
    height: 60%;
  }
  .search-input {
    margin-bottom: 30px !important;
    padding-left: 15px;
    padding-right: 15px;
  }
}

#app-toolbar-content {
  margin-right: 50px;
  .close-icon {
    position: absolute;
    right: 10px;
    top: 10px;
  }
}

.left-shadow {
  box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 20px;
}
</style>
