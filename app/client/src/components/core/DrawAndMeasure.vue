<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-card-title primary-title>
        <span class="title font-weight-regular">Measure and Draw</span>
      </v-card-title>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
        <v-divider></v-divider>
      </v-card-text>
      <v-subheader> Measure </v-subheader>
      <v-divider></v-divider>

      <!-- Measure -->
      <v-expansion-panel class="elevation-0">
        <v-expansion-panel-content
          expand-icon=""
          readonly
          v-for="item in measureItems"
          :key="item.id"
          :class="{
            'expansion-panel__container--active': activeId === item.id
          }"
          @click.native="toggle(item.id)"
        >
          <div slot="header">
            <v-layout row>
              <v-flex xs2>
                <v-icon
                  small
                  left
                  :class="{ activeIcon: activeId === item.id }"
                  >{{ item.icon }}</v-icon
                >
              </v-flex>
              <v-flex xs10>
                <span>{{ item.text }}</span>
              </v-flex>
            </v-layout>
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-divider class="mb-3"></v-divider>

      <!-- Draw -->
      <v-subheader> Draw </v-subheader>
      <v-divider></v-divider>
      <v-expansion-panel class="elevation-0">
        <v-expansion-panel-content
          expand-icon=""
          v-for="item in drawItems"
          :key="item.id"
          :class="{
            'expansion-panel__container--active': activeId === item.id
          }"
          @click.native="toggle(item.id)"
        >
          <div slot="header">
            <v-layout row>
              <v-flex xs2>
                <v-icon
                  small
                  left
                  :class="{ activeIcon: activeId === item.id }"
                  >{{ item.icon }}</v-icon
                >
              </v-flex>
              <v-flex xs8>
                <span>{{ item.text }}</span>
              </v-flex>
              <v-flex xs2>
                <v-icon class="close" v-bind:ref="item.id">{{
                  activeId === item.id ? "close" : ""
                }}</v-icon>
              </v-flex>
            </v-layout>
          </div>
          <v-card @click.stop="doNothing" class="card">
            <v-card-text
              >Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
              enim ad minim veniam, quis nostrud exercitation ullamco laboris
              nisi ut aliquip ex ea commodo consequat.</v-card-text
            >
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-divider></v-divider>

      <v-card-text> </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" color="green" @click="clear">Clear</v-btn>
      </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
export default {
  data: () => ({
    measureItems: [
      {
        id: 1,
        icon: "fas fa-ruler",
        text: "Length"
      },
      {
        id: 2,
        icon: "fas fa-ruler-combined",
        text: "Area"
      }
    ],
    drawItems: [
      {
        id: 3,
        icon: "far fa-dot-circle",
        text: "Point"
      },
      {
        id: 4,
        icon: "far fa-dot-circle",
        text: "Point with coordinates"
      },
      {
        id: 5,
        icon: "fas fa-project-diagram",
        text: "Line"
      },
      {
        id: 6,
        icon: "fas fa-draw-polygon",
        text: "Polygon"
      },
      {
        id: 7,
        icon: "fas fa-font",
        text: "Label"
      }
    ],
    activeId: undefined
  }),
  components: {},
  computed: {},
  methods: {
    toggle(id) {
      //1- Set active index of clicked item or remove it
      if (this.activeId === id) {
        this.activeId = undefined;
      } else {
        this.activeId = id;
      }
    },
    doNothing() {},
    clear() {
      if (this.activeId !== undefined) {
        //Option only for draw section items.
        let el = this.$refs[this.activeId];
        if (el) el[0].$el.click();
        this.activeId = undefined;
      }
    }
  },
  mounted() {}
};
</script>
<style lang="css" scoped>
.close {
  position: absolute;
  right: 10px;
  color: white;
}
.expansion-panel__container--active {
  background-color: #4caf50 !important;
  color: white !important;
  font-weight: bold !important;
}
.card {
  font-weight: normal !important;
}
.activeIcon {
  font-size: 20px;
  color: white;
}
</style>
