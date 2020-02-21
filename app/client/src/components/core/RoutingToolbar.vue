<template>
  <div class="elevation-2" style="z-index:2;">
    <v-toolbar flat height="50" color="white">
      <div v-for="(item, key, index) in routing.options" :key="index">
        <v-tooltip top>
          <template v-slot:activator="{ on }">
            <v-btn height="40" width="40" v-on="on" icon>
              <v-icon>{{ icons[key] ? icons[key] : "" }}</v-icon>
            </v-btn>
          </template>
          <span>{{ $t(`map.tooltips.routingProfiles.${key}`) }}</span>
        </v-tooltip>
        <v-menu
          origin="center center"
          :close-on-content-click="false"
          open-on-hover
          auto
          v-if="item.options.length > 0"
          offset-y
        >
          <template v-slot:activator="{ on }">
            <v-icon class="mt-4 mr-4" v-on="on">fas fa-sort-down</v-icon>
          </template>
          <v-card>
            <v-radio-group class="dropdown mb-0 pb-0">
              <v-radio
                class="ml-2 mt-2"
                v-for="r in item.options"
                :key="r"
                :label="r"
                :value="r"
              ></v-radio>
            </v-radio-group>
          </v-card>
        </v-menu>
      </div>
    </v-toolbar>
  </div>
</template>

<script>
export default {
  data: () => ({
    routingProfile: null,
    profileOption: null,
    icons: {
      walking: "fas fa-walking",
      cycling: "fas fa-biking",
      wheelchair: "fas fa-wheelchair"
    },
    routing: {
      default: "walking",
      options: {
        walking: {
          default: "standard",
          options: ["standard", "elderly"]
        },
        cycling: {
          default: "standard",
          options: ["standard", "pedelec"]
        },
        wheelchair: {
          options: []
        }
      }
    }
  })
};
</script>
<style lang="css" scoped>
.dropdown >>> .v-messages {
  min-height: 0px;
}
</style>
