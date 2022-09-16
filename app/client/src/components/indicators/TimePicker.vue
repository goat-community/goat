<template>
  <v-dialog
    width="400"
    overlay-opacity="0"
    persistent
    no-click-animation
    hide-overlay
    v-model="dialog"
    content-class="v-dialog"
  >
    <v-card
      v-draggable="draggableValue"
      ondragstart="return true;"
      :style="[isExpanded ? { height: 'auto' } : { height: '50px' }]"
      style="position:fixed;top:20px;left:380px;z-index:2;min-width:350px;max-width:450px;height:450px;overflow:hidden;"
    >
      <v-layout justify-space-between column fill-height>
        <v-app-bar
          :color="appColor.primary"
          height="50"
          style="cursor:grab;"
          dark
          :ref="handleId"
        >
          <v-app-bar-nav-icon>
            <v-icon style="color:#ffffff;">
              fas fa-bullseye
            </v-icon>
          </v-app-bar-nav-icon>
          <v-toolbar-title>
            <b>{{ $t("indicators.indicatorTimePicker") }}</b>
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-icon @click="expand" class="toolbar-icons mr-2">
            {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}
          </v-icon>
          <v-icon @click="close" class="toolbar-icons ml-2">
            fas fa-times
          </v-icon>
        </v-app-bar>
        <v-card-text class="pa-3">
          <v-select
            class="mb-2"
            :items="weekdays"
            v-model="weekday"
            :label="$t(`weekday`)"
            item-value="value"
            item-text="text"
            hide-details
          >
            <template slot="selection" slot-scope="{ item }">
              <v-row>
                <v-col cols="12" class="py-0"
                  ><span class="cb-item">{{
                    $t(`daysOfWeek.${item.text}`)
                  }}</span></v-col
                >
              </v-row>
            </template>
            <template slot="item" slot-scope="{ item }">
              <v-row>
                <v-col cols="12"
                  ><span class="cb-item">{{
                    $t(`daysOfWeek.${item.text}`)
                  }}</span></v-col
                >
              </v-row>
            </template>
          </v-select>
          <v-row>
            <v-col cols="6">
              <v-menu
                ref="indicator_time_from"
                v-model="fromTimeMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                max-width="250px"
                min-width="250px"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="fromTime"
                    :label="$t('fromTime')"
                    class="mb-0 pb-0"
                    prepend-inner-icon="fas fa-clock"
                    readonly
                    v-bind="attrs"
                    hide-details
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  v-if="fromTimeMenu"
                  full-width
                  :color="appColor.primary"
                  v-model="fromTime"
                  no-title
                  lazy
                  @click:minute="$refs.indicator_time_from.save(fromTime)"
                ></v-time-picker>
              </v-menu>
            </v-col>
            <v-col cols="6">
              <v-menu
                ref="indicator_time_to"
                v-model="toTimeMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                max-width="250px"
                min-width="250px"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="toTime"
                    :label="$t('toTime')"
                    class="mb-0 pb-0"
                    prepend-inner-icon="fas fa-clock"
                    readonly
                    hide-details
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  v-if="toTimeMenu"
                  full-width
                  :color="appColor.primary"
                  v-model="toTime"
                  no-title
                  lazy
                  @click:minute="$refs.indicator_time_to.save(toTime)"
                ></v-time-picker>
              </v-menu>
            </v-col>
          </v-row>
          <v-row v-if="isAlertVisible" class="my-0 pb-0">
            <v-spacer></v-spacer>
            <v-alert dense outlined type="error" class="mb-0">
              {{ $t("indicators.timePickerErrorMessage") }}
            </v-alert>
            <v-spacer></v-spacer>
          </v-row>
        </v-card-text>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { Draggable } from "draggable-vue-directive";
import { mapFields } from "vuex-map-fields";
export default {
  props: ["status", "translate"],
  directives: {
    Draggable
  },
  data() {
    return {
      weekdays: [
        { text: "monday", value: 1 },
        { text: "tuesday", value: 2 },
        { text: "wednesday", value: 3 },
        { text: "thursday", value: 4 },
        { text: "friday", value: 5 },
        { text: "saturday", value: 6 },
        { text: "sunday", value: 7 }
      ],
      fromTimeMenu: false,
      toTimeMenu: false,
      fromTime: "07:00",
      toTime: "08:00",
      weekday: 0,
      dialog: this.status,
      isExpanded: true,
      isAlertVisible: false,
      handleId: "handle-id",
      draggableValue: {
        handle: undefined,
        boundingElement: undefined,
        resetInitialPos: undefined
      }
    };
  },
  methods: {
    close() {
      this.dialog = false;
      this.$emit("changeStatus", this.dialog);
    },
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    validate() {
      let toTime = this.toTime.split(":");
      const toTimeInSeconds = toTime[0] * 3600 + toTime[1] * 60;
      let fromTime = this.fromTime.split(":");
      const fromTimeInSeconds = fromTime[0] * 3600 + fromTime[1] * 60;
      if (toTimeInSeconds < fromTimeInSeconds) {
        this.isAlertVisible = true;
        return false;
      } else {
        this.timeIndicators.weekday = this.weekday;
        this.timeIndicators.startTime = fromTimeInSeconds;
        this.timeIndicators.endTime = toTimeInSeconds;
        this.$emit("updateTimeIndicators");
        this.isAlertVisible = false;
        return true;
      }
    }
  },
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
    this.weekday = this.timeIndicators.weekday;
    const fromTime = new Date(0);
    fromTime.setSeconds(this.timeIndicators.startTime);
    this.fromTime = fromTime.toISOString().substring(11, 16);
    const toTime = new Date(0);
    toTime.setSeconds(this.timeIndicators.endTime);
    this.toTime = toTime.toISOString().substring(11, 16);
  },
  watch: {
    fromTime() {
      this.validate();
    },
    toTime() {
      this.validate();
    },
    weekday() {
      this.validate();
    }
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    ...mapFields("app", {
      timeIndicators: "timeIndicators"
    })
  }
};
</script>

<style>
.v-dialog {
  box-shadow: none;
}
</style>
