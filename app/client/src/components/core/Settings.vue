<template>
  <v-dialog v-model="show" scrollable max-width="500px">
    <v-card flat>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon><v-icon>fas fa-cog</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{ $t("appBar.settings.title") }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <!-- App Language Settings -->
        <v-subheader
          ><h3>{{ $t("appBar.settings.language") }}</h3></v-subheader
        >
        <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
          <v-divider></v-divider>
        </v-card-text>
        <v-card-text>
          <div class="">
            <span>
              <v-btn-toggle v-model="defaultLanguage" mandatory>
                <v-btn
                  text
                  v-for="entry in languages"
                  :key="entry.title"
                  @click="changeLocale(entry.language)"
                >
                  <flag :iso="entry.flag" v-bind:squared="false" />
                  <span class="pl-2">{{ entry.title }}</span>
                </v-btn>
              </v-btn-toggle>
            </span>
          </div>
        </v-card-text>
        <!-- Map Units Settings  -->
        <!-- <v-subheader
          ><h3>{{ $t("appBar.settings.units.header") }}</h3></v-subheader
        >
        <v-card-text class="pr-16 pl-16 pt-0 pb-0">
          <v-divider></v-divider>
        </v-card-text>
        <v-card-text>
          <v-radio-group v-model="units" row style="justify-content: center;">
            <v-radio
              :label="$t('appBar.settings.units.km')"
              value="kilometers"
            ></v-radio>
            <v-radio
              :label="$t('appBar.settings.units.miles')"
              value="miles"
            ></v-radio>
          </v-radio-group>
        </v-card-text> -->
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>
<script>
import i18n from "@/plugins/i18n";
import { EventBus } from "../../EventBus";
export default {
  props: ["visible"],
  data() {
    return {
      defaultLanguage: 0,
      units: "kilometers",
      languages: [
        { flag: "us", language: "en", title: "English" },
        { flag: "de", language: "de", title: "German" },
        { flag: "es", language: "es", title: "Español" },
        { flag: "al", language: "al", title: "Shqip" }
      ],
      interactionType: "languageChange"
    };
  },
  methods: {
    changeLocale(locale) {
      i18n.locale = locale;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", this.interactionType);
    }
  },
  computed: {
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    }
  }
};
</script>
