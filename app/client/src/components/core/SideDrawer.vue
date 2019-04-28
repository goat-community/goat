<template>
  <v-navigation-drawer
    id="sidebar-drawer"
    v-model="drawer"
    app
    dark
    persistent
    right
    hide-overlay
    class="green"
    width="50"
  >
    <v-layout justify-space-between column fill-height>
      <v-list>
        <template v-for="(item, index) in upItems">
          <v-list-tile
            @click="showHideModule"
            :key="index"
            active-class="red--text"
          >
            <v-list-tile-action>
              <v-icon color="white" light v-html="item.icon"></v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title v-html="item.text"></v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </template>
      </v-list>

      <v-list justify-end>
        <template v-for="(item, index) in bottomItems">
          <v-list-tile @click="showHideModule" :key="index">
            <v-list-tile-action>
              <v-icon color="white" light v-html="item.icon"></v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title v-html="item.text"></v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </template>
      </v-list>
    </v-layout>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import {} from "vuex";
export default {
  name: "app-sidebar",
  data: () => ({
    drawer: true,
    upItems: [
      {
        icon: "fas fa-user",
        text: "Login"
      },
      {
        icon: "fas fa-print",
        text: "Print"
      },
      {
        icon: "fas fa-paint-brush",
        text: "Draw and Measure"
      },
      {
        icon: "fas fa-filter",
        text: "Typography"
      },
      {
        icon: "fas fa-edit",
        text: "Edit"
      }
    ],
    bottomItems: [
      {
        icon: "fas fa-info-circle",
        text: "Info"
      },
      {
        icon: "fas fa-cog",
        text: "Settings"
      }
    ],
    responsive: false
  }),
  computed: {},
  mounted() {},
  beforeDestroy() {},
  methods: {
    showHideModule(evt) {
      console.log(evt);
    }
  }
};
</script>

<style lang="scss">
#sidebar-drawer {
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
</style>
