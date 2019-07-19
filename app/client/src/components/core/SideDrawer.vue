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
      class="green"
      width="50"
    >
      <v-layout justify-space-between column fill-height>
        <v-list>
          <template v-for="(item, index) in upItems">
            <v-list-item
              @click="toggleComponent(item.componentToShow)"
              :key="index"
              active-class="red--text"
            >
              <v-list-item-action>
                <v-icon
                  :style="
                    activeUpComponent === item.componentToShow
                      ? 'color: #30c2ff;'
                      : 'color: white'
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
        </v-list>
        <v-list justify-end>
          <template v-for="(item, index) in bottomItems">
            <v-list-item
              @click="toggleDialog(item.componentToShow)"
              :key="index"
            >
              <v-list-item-action>
                <v-icon color="white" light v-html="item.icon"></v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title v-html="item.text"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-list>
      </v-layout>
    </v-navigation-drawer>

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
import {} from "vuex";

import Login from "./Login";
import Settings from "./Settings";
import About from "./About";

import Print from "../print/Print";
import DrawAndMeasure from "../drawAndMeasure/DrawAndMeasure";
import Filter from "../layers/filter/Filter";
import Edit from "../layers/edit/Edit";

export default {
  name: "app-sidebar",
  components: {
    "map-print": Print,
    "map-login": Login,
    "map-draw-measure": DrawAndMeasure,
    "map-filter": Filter,
    "map-edit": Edit,
    "app-settings": Settings,
    "app-about": About
  },
  data: () => ({
    upItems: [
      {
        icon: "fas fa-user",
        text: "Login",
        componentToShow: "map-login"
      },
      {
        icon: "fas fa-print",
        text: "Print",
        componentToShow: "map-print"
      },
      {
        icon: "fas fa-paint-brush",
        text: "Draw and Measure",
        componentToShow: "map-draw-measure"
      },
      {
        icon: "fas fa-filter",
        text: "Filter",
        componentToShow: "map-filter"
      },
      {
        icon: "fas fa-edit",
        text: "Edit",
        componentToShow: "map-edit"
      }
    ],
    bottomItems: [
      {
        icon: "fas fa-cog",
        text: "Settings",
        componentToShow: "app-settings"
      },
      {
        icon: "fas fa-info-circle",
        text: "Info",
        componentToShow: "app-about"
      }
    ],
    container: false,
    activeUpComponent: "",
    activeBottomComponent: "",
    responsive: false,
    showDialog: false
  }),
  computed: {},
  mounted() {},
  beforeDestroy() {},
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
    hide() {
      this.container = false;
      this.activeUpComponent = "";
      this.activeBottomComponent = "";
      this.showDialog = false;
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
  padding-right: 50px;
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
