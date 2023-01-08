import Vue from "vue";
import VueI18n from "vue-i18n";
import axios from "axios";

Vue.use(VueI18n);

function loadLocaleMessages() {
  let languages = ["en", "de", "fr", "es"];
  const messages = {};
  languages.forEach(language => {
    axios
      .get(
        `https://goat-community.github.io/translations/Translations/${language.split(
          "-"
        )[0] ||
          process.env.VUE_APP_I18N_LOCALE ||
          "en"}/allTranslations.json`
      )
      .then(data => {
        messages[language] = data.data;
      });
  });
  return messages;
}

export default new VueI18n({
  locale:
    navigator.language.split("-")[0] || process.env.VUE_APP_I18N_LOCALE || "en",
  fallbackLocale: process.env.VUE_APP_I18N_FALLBACK_LOCALE || "en",
  messages: loadLocaleMessages()
});
