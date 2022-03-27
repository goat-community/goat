<template>
  <v-flex xs12 sm8 md4>
    <v-card class="px-16 mx-4 py-0 mb-2 fill-height" flat>
      <v-subheader> </v-subheader>

      <v-row no-gutters class="mb-4">
        <v-col justify="center" align="center" cols="4">
          <v-row no-gutters justify="center" align="center" class="fill-height">
            <v-avatar size="60">
              <v-icon large class="fa-solid fa-user"></v-icon>
            </v-avatar>
          </v-row>
        </v-col>

        <v-col cols="8">
          <v-row no-gutters align="center" class="fill-height">
            <p class="mb-0 header-name">
              {{
                `${user.name || userCopy.name}, ${user.surname ||
                  userCopy.surname}`
              }}
            </p>
            <p class="mb-0 sub-header">
              {{ `${user.email || userCopy.email}` }}
            </p>
          </v-row>
        </v-col>
      </v-row>

      <v-divider></v-divider>
      <v-select
        class="mt-8"
        v-model="studyAreaId"
        :items="studyAreaList"
        item-value="id"
        item-text="name"
        :label="$t('userSettings.changeStudyAreaTitle')"
        @change="changeStudyArea"
      >
      </v-select>
      <v-divider></v-divider>
      <v-select
        class="mt-2"
        :value="$i18n.locale"
        :items="languages"
        item-value="language"
        item-text="title"
        :label="$t('userSettings.uiLanguage')"
        @change="changeLocale"
      >
      </v-select>
      <v-btn
        style="text-transform:none;justify-content:left;"
        width="100%"
        class="mt-0"
        text
        @click="openContactSupportInNewTab"
      >
        <v-icon class="light-icon-color" left>
          fas fa-comments-question
        </v-icon>
        <span class="ml-2  theme--light">
          {{ $t("userSettings.contactSupport") }}
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
          {{ $t("userSettings.logout") }}
        </span>
      </v-btn>
      <v-divider></v-divider>
      <p class="mt-5 mb-1 sub-header">
        {{ (uploadedStorageSize / 1024).toFixed(2)
        }}{{ $t("userSettings.mbOf") }}
        {{
          parseInt(
            user.storage ? user.storage / 1024 : userCopy.storage / 1024
          )
        }}{{ $t("userSettings.mbUsed") }}
      </p>
      <v-progress-linear
        height="2"
        :color="appColor.secondary"
        :value="occupiedStoragePercentage"
        class="mb-6 mt-0 pt-0"
      ></v-progress-linear>
      <p class="mt-2 sub-header">
        {{ $t("userSettings.scenarios") }}: {{ scenarios.length }} /
        {{ limitScenarios }}
      </p>
    </v-card>
    <v-spacer></v-spacer>
    <confirm ref="confirm"></confirm>
  </v-flex>
</template>

<script>
import { mapGetters } from "vuex";
import { LOGOUT } from "../../store/actions.type";
import i18n from "@/plugins/i18n";
import { EventBus } from "../../EventBus";
import ApiService from "../../services/api.service";
import { mapFields } from "vuex-map-fields";

export default {
  data: () => ({
    languages: [
      { flag: "gb", language: "en", title: "English" },
      { flag: "de", language: "de", title: "Deutsch" }
    ],
    interactionType: "languageChange",
    studyAreaId: null,
    userCopy: {}
  }),
  computed: {
    ...mapGetters("auth", { user: "currentUser" }),
    ...mapGetters("app", {
      appColor: "appColor",
      occupiedStoragePercentage: "occupiedStoragePercentage",
      uploadedStorageSize: "uploadedStorageSize"
    }),
    ...mapGetters("map", {
      studyAreaList: "studyAreaList"
    }),
    ...mapGetters("scenarios", {
      scenarios: "scenarios",
      limitScenarios: "limitScenarios"
    }),
    ...mapGetters("isochrones", {
      calculations: "calculations"
    }),
    ...mapFields("auth", {
      userState: "user"
    })
  },
  methods: {
    changeLocale(locale) {
      i18n.locale = locale;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", this.interactionType);
      if (this.contextmenu) {
        this.contextmenu.close();
      }
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
      // Save language change
      ApiService.put("/users/me/preference", {
        language_preference: locale
      });
    },
    openContactSupportInNewTab() {
      let url = "https://plan4better.de/kontakt/";
      if (url) {
        window.open(url, "_blank");
      }
    },
    changeStudyArea(newStudyArea) {
      if (newStudyArea === this.user.active_study_area_id) {
        return;
      }
      if (this.calculations.length > 0) {
        this.$refs.confirm
          .open(
            this.$t("userSettings.changeStudyAreaTitle"),
            this.$t("userSettings.changeStudyAreaMessageWarning"),
            { color: this.appColor.primary, icon: "fa-solid fa-retweet" }
          )
          .then(confirm => {
            if (confirm) {
              ApiService.put("/users/me/preference", {
                active_study_area_id: newStudyArea
              }).then(() => {
                window.location.reload();
              });
            } else {
              this.studyAreaId = this.user.active_study_area_id;
            }
          });
      } else {
        ApiService.put("/users/me/preference", {
          active_study_area_id: newStudyArea
        }).then(() => {
          window.location.reload();
        });
      }
    },
    logout() {
      this.$store.dispatch(`auth/${LOGOUT}`);
      window.location.reload();
    }
  },
  created() {
    this.studyAreaId = this.user.active_study_area_id;
    this.userCopy = JSON.parse(JSON.stringify(this.user)); // Workaround for logout clean
  }
};
</script>

<style scoped></style>
