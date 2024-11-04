"use client";

import { de, enUS } from "date-fns/locale";
import i18next from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import resourcesToBackend from "i18next-resources-to-backend";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import type { UseTranslationOptions } from "react-i18next";
import { initReactI18next, useTranslation as useTranslationOrg } from "react-i18next";

import { getOptions, languages } from "./settings";

const runsOnServerSide = typeof window === "undefined";

//
i18next
  .use(initReactI18next)
  .use(LanguageDetector)
  .use(
    resourcesToBackend(
      (language: string, namespace: string) => import(`./locales/${language}/${namespace}.json`)
    )
  )
  .init({
    ...getOptions(),
    lng: undefined,
    detection: {
      order: ["path", "htmlTag", "cookie", "navigator"],
    },
    preload: runsOnServerSide ? languages : [],
  });

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useTranslation(ns?: string | string[], options?: UseTranslationOptions<any>) {
  const params = useParams();
  const lng = typeof params.lng === "string" ? params.lng : "en";

  const ret = useTranslationOrg(ns, options);
  const { i18n } = ret;
  if (runsOnServerSide && lng && i18n.resolvedLanguage !== lng) {
    i18n.changeLanguage(lng);
  } else {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [activeLng, setActiveLng] = useState<string | undefined>(i18n.resolvedLanguage);

    // eslint-disable-next-line react-hooks/rules-of-hooks
    useEffect(() => {
      if (activeLng === i18n.resolvedLanguage) return;
      setActiveLng(i18n.resolvedLanguage);
    }, [activeLng, i18n.resolvedLanguage]);

    // eslint-disable-next-line react-hooks/rules-of-hooks
    useEffect(() => {
      if (!lng || i18n.resolvedLanguage === lng) return;
      i18n.changeLanguage(lng);
    }, [lng, i18n]);
  }
  return ret;
}

export function useDateFnsLocale() {
  const { i18n } = useTranslation();
  return i18n?.language === "de" ? de : enUS;
}
