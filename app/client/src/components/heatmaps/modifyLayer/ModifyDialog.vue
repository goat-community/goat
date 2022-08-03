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
      style="position:fixed;top:10px;left:360px;z-index:2;min-width:350px;max-width:450px;height:450px;overflow:hidden;"
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
            <b>Indicator Control</b>
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
            :items="selectedDay"
            :value="currentDay"
            @change="dayChange"
            label="Weekdays"
          ></v-select>
          <v-row>
            <v-col cols="6">
              <v-text-field
                @change="startTimeChanged"
                label="From Time"
                :value="`${startHour}:00`"
                type="time"
              >
              </v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                @change="endTimeChanged"
                label="To Time"
                :value="`${endHour}:00`"
                type="time"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { Draggable } from "draggable-vue-directive";

export default {
  props: ["status", "translate"],
  directives: {
    Draggable
  },
  data() {
    return {
      selectedDay: [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
      ],
      dialog: this.status,
      currentDay: null,
      startHour: "",
      endHour: "",
      isExpanded: true,
      handleId: "handle-id",
      draggableValue: {
        handle: undefined,
        boundingElement: undefined,
        resetInitialPos: undefined
      }
    };
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    })
  },
  methods: {
    close() {
      this.dialog = false;
      this.$emit("changeStatus", this.dialog);
    },
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    dayChange(e) {
      let dayNr = 0;
      switch (e) {
        case "Sunday":
          dayNr = 7;
          break;
        case "Monday":
          dayNr = 1;
          break;
        case "Tuesday":
          dayNr = 2;
          break;
        case "Wednesday":
          dayNr = 3;
          break;
        case "Thursday":
          dayNr = 4;
          break;
        case "Friday":
          dayNr = 5;
          break;
        case "Saturday":
          dayNr = 6;
          break;
        default:
          break;
      }
      console.log(dayNr);
    },
    startTimeChanged(e) {
      let hours = parseInt(e.split(":")[0]);
      let minutes = parseInt(e.split(":")[1]);
      let allMinutes = (hours * 60 + minutes) * 60;
      console.log(allMinutes);
    },
    endTimeChanged(e) {
      let hours = parseInt(e.split(":")[0]);
      let minutes = parseInt(e.split(":")[1]);
      let allMinutes = (hours * 60 + minutes) * 60;
      console.log(allMinutes);
    }
  },
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];

    this.currentDay = "Monday";
    this.startHour = "07:00";
    this.endHour = "09:00";
  }
};
</script>

<style>
.v-dialog {
  box-shadow: none;
}
</style>
