import i18n from "i18next";
import { initReactI18next } from "react-i18next";

// Locale files
import germanFile from "../locales/de.json";
import englishFile from "../locales/en.json";

i18n.use(initReactI18next).init({
  resources: getTranslations(),
  debug: true,
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

function getTranslations() {
  const languagesSorted = {
    en: englishFile,
    de: germanFile,
  };
  const messages = {};
  for (const language in languagesSorted) {
    messages[language] = { translation: languagesSorted[language] };
  }
  return messages;
}

export default i18n;
