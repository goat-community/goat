<template>
  <v-dialog v-model="show" scrollable max-width="355px">
    <v-card>
      <v-app-bar :color="color" height="50" dark>
        <v-app-bar-nav-icon><v-icon>query_builder</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>Opening Hours</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <v-btn
          class="ml-2 my-2"
          v-show="!isEditing && osmHoursString == ''"
          @click="addOpeningHours"
          >Add Opening Hours</v-btn
        >
        <div v-if="osmHoursString != ''">
          <div v-show="isEditing">
            <v-tabs v-model="activeTab" v-if="isEditing" grow>
              <v-tab>{{ $t(`openingHours.openingTime`) }}</v-tab>
              <v-tab>{{ $t(`openingHours.closingTime`) }}</v-tab>
            </v-tabs>
            <!-- Opening Hours  -->
            <v-time-picker
              v-show="activeTab === 0"
              v-model="editTimeSelector.opens"
              format="24hr"
              :color="color"
              full-width
              class="elevation-0"
            ></v-time-picker>
            <!-- Closing Hours -->
            <v-time-picker
              v-show="activeTab === 1"
              v-model="editTimeSelector.closes"
              format="24hr"
              :color="color"
              full-width
              class="elevation-0"
            ></v-time-picker>
          </div>
          <div v-show="!isEditing">
            <v-container class="pb-0" fluid>
              <v-layout row>
                <!-- <v-btn
                  class="white--text ml-2"
                  small
                  color="error"
                  @click="clear()"
                >
                  <v-icon left>delete</v-icon>{{ $t("buttonLabels.remove") }}
                </v-btn> -->

                <span class="body-1 ml-3 pt-1">{{
                  $t(`openingHours.default`)
                }}</span>
                <v-chip class="mx-2" @click="openTimeSelector()">
                  <v-avatar left>
                    <v-icon class="text-xs-center">fas fa-clock</v-icon>
                  </v-avatar>
                  <strong>{{ getDefaultTime }}</strong>
                </v-chip>
              </v-layout>
              <v-divider class="mt-2 mb-2"></v-divider>
              <template v-for="(weekday, index) in openingHours">
                <v-layout :key="index" row>
                  <v-flex xs7>
                    <v-checkbox
                      class="ml-2 pb-0 mb-0"
                      v-model="weekday.isOpen"
                      :label="$t(`openingHours.${index}`)"
                    ></v-checkbox>
                  </v-flex>
                  <v-flex xs5>
                    <v-chip
                      v-if="weekday.isOpen"
                      small
                      :color="
                        (weekday.hours.opens !== null &&
                          weekday.hours.opens !== defaultHours.opens) ||
                        (weekday.hours.closes !== null &&
                          weekday.hours.closes !== defaultHours.closes)
                          ? 'orange'
                          : 'gray'
                      "
                      @click="openTimeSelector(index)"
                    >
                      <v-avatar left>
                        <v-icon small class="text-xs-center"
                          >fas fa-clock</v-icon
                        >
                      </v-avatar>
                      <strong>
                        {{
                          weekday.hours.opens && weekday.hours.closes
                            ? `${weekday.hours.opens} - ${weekday.hours.closes}`
                            : `${defaultHours.opens} - ${defaultHours.closes}`
                        }}</strong
                      >
                    </v-chip>
                  </v-flex>
                </v-layout>
              </template>
            </v-container>
          </div>
          <v-card-actions v-show="isEditing" class="pt-0">
            <v-card-text class="red--text"
              ><strong>{{
                $t(`openingHours.${selectedDay ? selectedDay : "default"}`)
              }}</strong></v-card-text
            >
            <v-spacer></v-spacer>
            <v-btn
              color="primary darken-1"
              :disabled="
                editTimeSelector.opens && editTimeSelector.closes ? false : true
              "
              text
              @click.native="ok"
              >{{ $t("buttonLabels.ok") }}</v-btn
            >
            <v-btn color="grey" text @click.native="cancel">{{
              $t("buttonLabels.cancel")
            }}</v-btn>
          </v-card-actions>
        </div>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    visible: { type: Boolean, required: true },
    color: { type: String, default: "#2BB381" },
    osmHours: {
      type: String,
      required: false,
      default: ""
    }
  },
  data: () => ({
    //
    defaultOsmHoursString: "Mo-Sa 08:00-18:00",
    osmHoursString: "",
    // Editing hours
    isEditing: false,
    selectedDay: null,
    activeTab: 0,
    editTimeSelector: {
      opens: null,
      closes: null
    },
    defaultHours: {
      opens: "8:00",
      closes: "18:00"
    },
    // Values.
    openingHours: {
      monday: {
        isOpen: true,
        hours: {
          opens: null,
          closes: null
        }
      },
      tuesday: {
        isOpen: true,
        hours: {
          opens: null,
          closes: null
        }
      },
      wednesday: {
        isOpen: true,
        hours: {
          opens: null,
          closes: null
        }
      },
      thursday: {
        isOpen: true,
        hours: {
          opens: null,
          closes: null
        }
      },
      friday: {
        isOpen: true,
        hours: {
          opens: null,
          closes: null
        }
      },
      saturday: {
        isOpen: true,
        hours: {
          opens: null,
          closes: null
        }
      },
      sunday: {
        isOpen: false,
        hours: {
          opens: null,
          closes: null
        }
      },
      publicHolidays: {
        isOpen: false,
        hours: {
          opens: null,
          closes: null
        }
      }
    }
  }),
  computed: {
    show: {
      get() {
        if (this.visible) {
          this.parseOsmHours();
        }
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.clear();
          this.$emit("close");
        }
      }
    },
    getDefaultTime() {
      const { opens, closes } = this.defaultHours;
      return `${opens} - ${closes}`;
    }
  },
  methods: {
    openTimeSelector(day) {
      this.selectedDay = day;
      this.isEditing = true;
      if (!day) {
        // Edit default time value
        this.editTimeSelector = { ...this.defaultHours };
      } else {
        // Edit time individual value
        const openingHours = this.openingHours[day].hours;
        this.editTimeSelector = openingHours.opens
          ? { ...openingHours }
          : { ...this.defaultHours };
      }
    },
    addOpeningHours() {
      // Add default osm hour
      this.osmHoursString = this.defaultOsmHoursString;
      this.parseOsmHours();
    },
    removeOpeningHours() {},
    parseOsmHours() {
      if (this.osmHours !== "") {
        this.osmHoursString = this.osmHours;
      }
      // If hours string is not empty extract the values..
    },
    ok() {
      if (!this.selectedDay) {
        // Save/Update default hours is not day is selected
        this.defaultHours = { ...this.editTimeSelector };
      } else {
        // Save/Update selected weekday
        this.openingHours[this.selectedDay].hours = {
          ...this.editTimeSelector
        };
      }
      this.resetEdit();
    },
    cancel() {
      this.resetEdit();
    },
    resetEdit() {
      this.isEditing = false;
      this.selectedDay = null;
      this.activeTab = 0;
    },
    clear() {
      this.resetEdit();
      this.osmHoursString = "";
      const reset = { opens: null, closes: null };
      this.editTimeSelector = { ...reset };
      Object.keys(this.openingHours).forEach(key => {
        this.openingHours[key].hours = { ...reset };
      });
    }
  }
};
</script>

<style scoped>
.v-card__text,
.v-card__title {
  word-break: normal !important;
}
.toggle-all >>> .v-input__control {
  height: 30px;
}
</style>
