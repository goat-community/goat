<template>
  <div class="elevation-2" style="z-index:2;">
    <v-toolbar v-if="routingData" flat height="50" color="white">
      <v-item-group v-model="route" mandatory>
        <v-row>
          <div v-for="(item, key, index) in routingData.options" :key="index">
            <v-item v-slot:default="{ active }">
              <!-- route buttons -->
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    :color="active ? '#30C2FF' : ''"
                    @click="onRouteBtnClick(key)"
                    height="40"
                    width="40"
                    v-on="on"
                    icon
                  >
                    <v-icon>{{ icons[key] ? icons[key] : "" }}</v-icon>
                  </v-btn>
                </template>
                <span>{{
                  $t(`map.tooltips.routingProfiles.${key}.title`)
                }}</span>
              </v-tooltip>
              <!-- -- -->
            </v-item>

            <!-- dropdown menus  -->
            <v-menu
              origin="center center"
              :close-on-content-click="false"
              close-delay="100"
              open-on-hover
              auto
              v-if="item.options.length > 0"
              offset-y
            >
              <template v-slot:activator="{ on }">
                <v-icon class="mt-4 mr-4" v-on="on">fas fa-sort-down</v-icon>
              </template>
              <v-card>
                <v-radio-group
                  v-model="activeRoutingProfile"
                  class="dropdown mb-0 pb-0"
                >
                  <v-radio
                    class="ml-2 mt-2"
                    v-for="(r, i) in item.options"
                    :key="i"
                    :value="`${key}_${r.value}`"
                    @change="onRouteProfileSelected(index, r)"
                  >
                    <template v-slot:label>
                      <span class="subtitle-1 font-weight-medium ">
                        {{
                          $te(
                            `map.tooltips.routingProfiles.${key}.options.${r.value}.title`
                          )
                            ? $t(
                                `map.tooltips.routingProfiles.${key}.options.${r.value}.title`
                              )
                            : r
                        }}</span
                      >

                      <v-spacer></v-spacer>

                      <!-- TOOLTIP FOR ROUTE PROFILE  -->
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-icon
                            v-on="on"
                            light
                            v-if="
                              $te(
                                `map.tooltips.routingProfiles.${key}.options.${r.value}.tooltip`
                              )
                            "
                            small
                            style="margin-top:2px;"
                            class="text-xs-right ml-4"
                            >fas fa-info-circle</v-icon
                          >
                        </template>
                        <span>{{
                          $t(
                            `map.tooltips.routingProfiles.${key}.options.${r.value}.tooltip`
                          )
                        }}</span>
                      </v-tooltip>
                      <!-- --- -->
                    </template>
                  </v-radio>
                </v-radio-group>
              </v-card>
            </v-menu>
            <!--  -->
          </div>
        </v-row>
      </v-item-group>
    </v-toolbar>
    <v-divider> </v-divider>
    <div class="text-center">
      <v-chip
        v-for="(item, index) in calculationModesOptions"
        style="cursor:pointer;width:100px;justify-content:center;"
        :color="calculationModes === item.value ? activeColor.primary : ''"
        @click="selectModus(item.value)"
        :key="index"
        :class="{
          'subtitle-2 ma-2': true,
          'white--text': calculationModes === item.value
        }"
      >
        {{ $t(`isochrones.options.${item.name}`) }}
      </v-chip>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { Isochrones } from "../../mixins/Isochrones";

export default {
  mixins: [Isochrones],
  data: () => ({
    route: null,
    routingData: null
  }),
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    ...mapGetters("isochrones", { icons: "routeIcons", options: "options" }),
    ...mapFields("isochrones", {
      activeRoutingProfile: "activeRoutingProfile",
      calculationModesOptions: "options.calculationModes.values",
      calculationModes: "options.calculationModes.active",
      speed: "options.speed"
    })
  },
  methods: {
    selectModus(item) {
      this.calculationModes = item;
      this.canCalculateScenario(this.calculationModes);
    },
    filterCalcModeValues() {
      return this.options.calculationModes.values;
    },
    onRouteProfileSelected(index, r) {
      this.route = index;
      if (r.speed) {
        this.speed = r.speed;
      }
    },
    onRouteBtnClick(key) {
      //Select route
      this.route = Object.keys(this.routingData.options).indexOf(key);
      //Select default profile
      const selectedOption = this.routingData.options[key];
      const defaultValue = selectedOption.default;
      this.activeRoutingProfile = defaultValue ? `${key}_${defaultValue}` : key;
      this.changeDefaultSpeed(selectedOption);
    },
    changeDefaultSpeed(selectedOption) {
      const selectedRadio = selectedOption.options.filter(v => {
        return v.value === selectedOption.default;
      });
      if (selectedRadio.length === 1 && selectedRadio[0].speed) {
        this.speed = selectedRadio[0].speed;
      } else if (selectedOption.speed) {
        this.speed = selectedOption.speed;
      }
    }
  },

  created() {
    this.routingData = this.$appConfig.componentData.routing;
    const options = this.routingData.options;
    const defaultRouteName = this.routingData.default;
    const routeOptions = Object.keys(options);
    this.route = routeOptions.indexOf(defaultRouteName);
    this.activeRoutingProfile = `${defaultRouteName}_${this.routingData.options[defaultRouteName].default}`;
    //Add timeout to be sure that isochrone option is loaded and it doesn't override the default speed from routing
    setTimeout(() => {
      this.changeDefaultSpeed(this.routingData.options[defaultRouteName]);
    }, 300);
  }
};
</script>
<style lang="css" scoped>
.dropdown >>> .v-messages {
  min-height: 0px;
}
.dropdown >>> .v-label {
  width: 100%;
}

.dropdown >>> .v-radio {
  margin-right: 10px;
}
</style>
