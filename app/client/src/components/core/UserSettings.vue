<template>
  <v-flex xs12 sm8 md4>
    <v-card class="px-16 mx-4 py-0 mb-2 fill-height" flat>
      <v-subheader> </v-subheader>

      <v-row no-gutters class="mb-4">
        <v-col justify="center" align="center" cols="4">
          <v-row no-gutters justify="center" align="center" class="fill-height">
            <v-avatar size="60">
              <v-icon class="fas fa-mountains"></v-icon>
            </v-avatar>
          </v-row>
        </v-col>

        <v-col cols="8">
          <v-row no-gutters align="center" class="fill-height">
            <p class="mb-0 header-name">
              {{ `${user.name}, ${user.surname}` }}
            </p>
            <p class="mb-0 sub-header">Institution / company</p>
            <p class="mb-0 sub-header">{{ `${user.email}` }}</p>
          </v-row>
        </v-col>
      </v-row>
      <v-divider></v-divider>
      <v-select
        class="mt-8"
        :value="studyAreaProps"
        return-object
        :items="studyAreaList"
        item-value="id"
        item-text="name"
        label="Study area"
        @change="changeStudyArea"
      >
      </v-select>
      <v-btn
        style="text-transform:none;justify-content:left;"
        width="100%"
        class="mt-3"
        text
        @click="openContactSupportInNewTab"
      >
        <v-icon class="light-icon-color" left>
          fas fa-comments-question
        </v-icon>
        <span class="ml-2  theme--light">
          Contact support
        </span>
      </v-btn>
      <br />
      <v-btn
        @click="logout"
        style="text-transform:none;justify-content:left;"
        width="100%"
        class="mt-3 mb-3"
        text
      >
        <v-icon class="light-icon-color" left>
          fas fa-arrow-right-from-bracket
        </v-icon>
        <span class="ml-2  theme--light">
          Logout
        </span>
      </v-btn>
      <v-divider></v-divider>
      <p class="mt-5 mb-1 sub-header">
        {{ (uploadedStorageSize / 1024).toFixed(1) }}MB of
        {{ parseInt(user.storage / 1024) }}MB used
      </p>
      <v-progress-linear
        height="2"
        :color="appColor.secondary"
        :value="occupiedStoragePercentage"
        class="mb-6 mt-0 pt-0"
      ></v-progress-linear>
      <p class="mt-2 sub-header">
        Scenarios: {{ scenarios.length }} / {{ limitScenarios }}
      </p>
    </v-card>
    <v-spacer></v-spacer>
  </v-flex>
</template>

<script>
import { mapGetters } from "vuex";
import { LOGOUT } from "../../store/actions.type";
export default {
  data: () => ({}),
  computed: {
    ...mapGetters("auth", { user: "currentUser" }),
    ...mapGetters("app", {
      appColor: "appColor",
      occupiedStoragePercentage: "occupiedStoragePercentage",
      uploadedStorageSize: "uploadedStorageSize"
    }),
    ...mapGetters("map", {
      studyAreaProps: "studyAreaProps",
      studyAreaList: "studyAreaList"
    }),
    ...mapGetters("scenarios", {
      scenarios: "scenarios",
      limitScenarios: "limitScenarios"
    })
  },
  methods: {
    openContactSupportInNewTab() {
      let url = "https://plan4better.de/kontakt/";
      if (url) {
        window.open(url, "_blank");
      }
    },
    changeStudyArea(newStudyArea) {
      if (newStudyArea.id === this.studyAreaProps.id) {
        return;
      }
    },
    logout() {
      this.$store.dispatch(`auth/${LOGOUT}`);
      window.location.reload();
    }
  }
};
</script>

<style scoped></style>
