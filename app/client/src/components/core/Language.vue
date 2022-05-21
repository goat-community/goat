<template>
  <v-speed-dial
    v-model="fab"
    direction="top"
    class="mb-2"
    transition="slide-y-reverse-transition"
  >
    <template v-slot:activator>
      <v-tooltip :disabled="fab === true" left>
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" small class="elevation-0 ma-0 pa-0">
            <country-flag
              :country="activeLanguage[0].flag || $i18n.locale"
              size="normal"
            />
          </v-btn>
        </template>
        <span>Change language</span>
      </v-tooltip>
    </template>

    <div>
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
import { mapGetters } from "vuex";

export default {
  props: ["visible"],

  data() {
    return {
      fab: false,
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
      if (this.contextmenu) {
        this.contextmenu.close();
      }
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
    }
  },
  computed: {
    ...mapGetters("map", {
      contextmenu: "contextmenu"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    notActiveLanguages() {
      const notActiveLanguages = this.languages.filter(value => {
        return value.language !== this.$i18n.locale;
      });
      return notActiveLanguages;
    },
    activeLanguage() {
      let activeLanguage = this.languages.filter(value => {
        return value.language === this.$i18n.locale;
      });
      if (activeLanguage.length === 0) {
        activeLanguage = this.languages.filter(
          value => value.language === "en"
        );
      }
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
