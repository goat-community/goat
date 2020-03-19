<template>
  <v-speed-dial
    v-model="fab"
    direction="top"
    class="mb-4"
    transition="slide-y-reverse-transition"
  >
    <template v-slot:activator>
      <v-tooltip :disabled="fab === true" left>
        <template v-slot:activator="{ on }">
          <v-btn
            dark
            v-on="on"
            small
            class="elevation-0 ma-0 pa-0"
            color="#4CAF50"
          >
            <country-flag
              :country="activeLanguage[0].flag || $i18n.locale"
              size="normal"
            />
          </v-btn>
        </template>
        <span>Change language</span>
      </v-tooltip>
    </template>

    <div style="background-color:#A1D5A3;">
      <v-btn
        class="ma-0 pa-0"
        text
        v-for="entry in notActiveLanguages"
        @click="changeLocale(entry.language)"
        :key="entry.title"
      >
        <country-flag :country="entry.flag" size="normal" />
      </v-btn>
    </div>
  </v-speed-dial>
</template>
<script>
import i18n from "@/plugins/i18n";
import { EventBus } from "../../EventBus";
export default {
  props: ["visible"],
  data() {
    return {
      fab: false,
      units: "kilometers",
      languages: [
        { flag: "gb", language: "en", title: "English" },
        { flag: "de", language: "de", title: "Deutsch" },
        { flag: "es", language: "es", title: "Español" }
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
    notActiveLanguages() {
      const notActiveLanguages = this.languages.filter(value => {
        return value.language !== this.$i18n.locale;
      });
      return notActiveLanguages;
    },
    activeLanguage() {
      const activeLanguage = this.languages.filter(value => {
        return value.language === this.$i18n.locale;
      });
      return activeLanguage;
    },
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
    }
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
