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
      persistent
      permanent
      right
      hide-overlay
      :class="{ 'left-shadow': container === false }"
      width="50"
    >
      <!-- TOP BUTTONS -->
      <v-layout justify-space-between column fill-height>
        <v-row no-gutters style="height:35%;" align-top>
          <v-list>
            <template v-for="(item, index) in topItems">
              <v-tooltip left :key="index">
                <template v-slot:activator="{ on }">
                  <v-list-item
                    :class="item.class"
                    @click="toggleComponent(item.componentToShow)"
                    v-on="on"
                    :style="getComponentButtonStyle(item)"
                  >
                    <v-list-item-action>
                      <v-icon
                        dense
                        :color="
                          activeUpComponent === item.componentToShow
                            ? 'white'
                            : 'rgba(0, 0, 0, 0.54)'
                        "
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
        </v-row>

        <!-- MIDDLE BUTTONS -->
        <v-row no-gutters style="height:55%;" align-center>
          <v-list>
            <template v-for="(item, index) in middleItems">
              <v-tooltip left :key="index">
                <template v-slot:activator="{ on }">
                  <v-list-item
                    @click="toggleComponent(item.componentToShow)"
                    v-on="on"
                    :style="[
                      activeUpComponent === item.componentToShow
                        ? { backgroundColor: appColor.primary }
                        : { backgroundColor: '' }
                    ]"
                  >
                    <v-list-item-action>
                      <v-icon
                        dense
                        :color="
                          activeUpComponent === item.componentToShow
                            ? 'white'
                            : 'rgba(0, 0, 0, 0.54)'
                        "
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
        </v-row>
        <!-- END BUTTONS -->
        <v-row no-gutters style="height:10%;">
          <!-- BOTTOM ITEMS -->
          <template v-for="(item, index) in bottomItems">
            <v-tooltip left :key="index">
              <template v-slot:activator="{ on }">
                <v-list-item
                  style="padding: 0 12px;"
                  @click="toggleDialog(item.componentToShow)"
                  v-on="on"
                >
                  <v-list-item-action>
                    <v-icon
                      light
                      v-html="item.icon"
                      color="rgba(0, 0, 0, 0.54)"
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
        </v-row>
      </v-layout>
    </v-navigation-drawer>
    <confirm ref="confirm"></confirm>

    <component
      :visible="showDialog"
      @close="showDialog = false"
      v-bind:is="activeBottomComponent"
    ></component>
    <!-- <app-about :visible="showDialog" @close="showDialog = false" /> -->
  </div>
</template>

<script>
// Utilities

import UserSettings from "./UserSettings";
import UserDataUpload from "./UserDataUpload";
import Settings from "./Settings";
import About from "./About";
import Print from "../print/Print";
import Filter from "../layers/filter/Filter";
import Edit from "../layers/edit/Edit";
import Language from "./Language";
import { mapGetters } from "vuex";

export default {
  name: "app-sidebar",
  components: {
    "user-settings": UserSettings,
    "user-data-upload": UserDataUpload,
    "map-print": Print,
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
    topItems() {
      return [
        {
          icon: "fas fa-circle-user",
          text: this.$t("appBar.buttons.user-settings"),
          componentToShow: "user-settings"
        },
        {
          icon: "fas fa-cloud",
          text: this.$t("appBar.buttons.user-data-upload"),
          componentToShow: "user-data-upload",
          class: "pl-3"
        }
      ];
    },
    middleItems() {
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
        }
      ];
    },
    bottomItems() {
      return [
        {
          icon: "fas fa-info-circle",
          text: this.$t("appBar.buttons.about"),
          componentToShow: "app-about"
        }
      ];
    },
    ...mapGetters("app", {
      appColor: "appColor",
      isRecomputingHeatmap: "isRecomputingHeatmap"
    }),
    ...mapGetters("map", {
      selectedLayer: "selectedEditLayer"
    })
  },
  methods: {
    toggleComponent(component) {
      if (
        (component === "user-data-upload" && this.selectedLayer) ||
        this.isRecomputingHeatmap
      ) {
        return;
      }
      if (component === this.activeUpComponent) {
        this.hide();
      } else {
        this.container = true;
        this.activeUpComponent = component;
      }
    },
    getComponentButtonStyle(item) {
      let style = "";
      if (this.activeUpComponent === item.componentToShow) {
        style += "background-color: " + this.appColor.primary + ";";
      }
      if (
        (item.componentToShow === "user-data-upload" && this.selectedLayer) ||
        this.isRecomputingHeatmap
      ) {
        style += "cursor: not-allowed;";
      }
      return style;
    },

    toggleDialog(component) {
      this.activeBottomComponent = component;
      this.showDialog = true;
    },
    hide() {
      this.container = false;
      this.activeUpComponent = "";
      this.activeBottomComponent = "";
      this.showDialog = false;
    }
  },
  watch: {
    isRecomputingHeatmap() {
      if (
        this.activeUpComponent === "user-data-upload" &&
        this.isRecomputingHeatmap
      ) {
        this.hide();
      }
    }
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
