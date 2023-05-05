import React from "react";
import { useTranslation, type getI18n } from "react-i18next";

export default function LocaleSwitcher() {
  const { i18n } = useTranslation();

  return <button onClick={() => changeLanguage(i18n)}> Change Language </button>;
}

function changeLanguage(i18n: ReturnType<typeof getI18n>) {
  return i18n.changeLanguage(i18n.language === "en" ? "de" : "en");
}
