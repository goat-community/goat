import i18next from "i18next";
import { describe, expect, it } from "vitest";

import de from "@/i18n/locales/de/common.json";
import en from "@/i18n/locales/en/common.json";

import { INPUT_CHOICE_LABEL_KEY } from "@/lib/utils/templates";

/**
 * The labels of a template's dataset choices (ship / copy / empty copy) and
 * of the copies made on use. Each one has to exist in both languages, and
 * the counted toasts need their plural forms, or i18next renders the raw key.
 */
const PLAIN_KEYS = [
  ...Object.values(INPUT_CHOICE_LABEL_KEY),
  "template_dataset_copy_hint",
  "template_dataset_handling",
  "template_copy_for_you",
  "layer_copy",
];
const COUNTED_KEYS = ["template_copies_hint", "template_copies_started", "template_copies_not_started"];

const translator = (language: "en" | "de") => {
  const instance = i18next.createInstance();
  instance.init({
    lng: language,
    fallbackLng: false,
    ns: ["common"],
    defaultNS: "common",
    resources: { en: { common: en }, de: { common: de } },
  });
  return instance;
};

const templateKeys = (messages: Record<string, unknown>) =>
  Object.keys(messages)
    .filter((key) => key.startsWith("template_"))
    .sort();

describe("template copy labels", () => {
  it.each(["en", "de"] as const)("%s names every dataset choice", (language) => {
    const t = translator(language);
    for (const key of PLAIN_KEYS) {
      const text = t.t(key);
      expect(text, key).not.toBe(key);
      expect(text.length).toBeGreaterThan(0);
    }
  });

  it.each(["en", "de"] as const)("%s resolves every counted copy message", (language) => {
    const t = translator(language);
    for (const key of COUNTED_KEYS) {
      for (const count of [1, 3]) {
        const text = t.t(key, { count });
        expect(text, key).not.toBe(key);
        expect(text).toContain(String(count));
      }
    }
  });

  it("gives both languages the same template keys", () => {
    expect(templateKeys(de as Record<string, unknown>)).toEqual(templateKeys(en as Record<string, unknown>));
  });

  it.each(["en", "de"] as const)("%s names a copy job after its dataset", (language) => {
    const text = translator(language).t("layer_copy_named", { name: "Vorhaben (Eingabe)" });
    expect(text).toContain("Vorhaben (Eingabe)");
    expect(text).not.toBe("layer_copy_named");
  });

  it("tells a read-only shipped dataset from a copy in German", () => {
    const t = translator("de");
    expect(t.t("template_dataset_ship")).toBe("Mitliefern (nur lesen)");
    expect(t.t("template_dataset_copy")).toBe("Kopie für jeden Nutzer (mit Inhalt)");
  });
});
