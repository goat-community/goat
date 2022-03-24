<template>
  <v-dialog v-model="show" scrollable max-width="500px">
    <v-card flat>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon><v-icon>fas fa-flag</v-icon></v-app-bar-nav-icon>
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
              <v-btn-toggle v-model="selectedLanguage" mandatory>
                <v-flex class="mx-2">
                  <v-btn
                    text
                    v-for="entry in languages"
                    :key="entry.title"
                    @click="changeLocale(entry.language)"
                  >
                    <!-- <flag :iso="entry.flag" v-bind:squared="false" /> -->
                    <span class="pl-2">{{ entry.title }}</span>
                  </v-btn>
                </v-flex>
              </v-btn-toggle>
            </span>
          </div>
        </v-card-text>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>
<script>
import i18n from "@/plugins/i18n";
import { EventBus } from "../../EventBus";
import { mapGetters } from "vuex";

export default {
  props: ["visible"],
  data() {
    return {
      selectedLanguage: 0,
      units: "kilometers",
      languages: [
        { flag: "gb", language: "en", title: "English" },
        { flag: "de", language: "de", title: "Deutsch" }
      ],
      interactionType: "languageChange"
    };
  },
  methods: {
    changeLocale(locale) {
      i18n.locale = locale;
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", this.interactionType);
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
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
          EventBus.$emit("ol-interaction-stoped", this.interactionType);
        }
      }
    },
    ...mapGetters("app", {
      appColor: "appColor"
    })
  },
  mounted() {
    const currentLang = this.$i18n.locale;

    this.languages.forEach((l, index) => {
      if (l.language === currentLang) {
        this.selectedLanguage = index;
      }
    });
  }
};
</script>
