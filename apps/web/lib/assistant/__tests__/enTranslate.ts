import en from "@/i18n/locales/en/common.json";

import type { Translate } from "@/lib/assistant/chips";

const EN = en as unknown as Record<string, string>;
const ESCAPED: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
  "/": "&#x2F;",
};

/**
 * The English texts with i18next's interpolation: `{{name}}` is replaced by the
 * option, HTML-escaped unless the call turns `escapeValue` off, as i18next does.
 */
export const enTranslate: Translate = (key, options = {}) => {
  const { interpolation, defaultValue, ...values } = options as Record<string, unknown>;
  const escape = (interpolation as { escapeValue?: boolean } | undefined)?.escapeValue !== false;
  // i18next's plural keys for English: `_one` for exactly one, `_other` otherwise.
  const plural =
    typeof values.count === "number" ? EN[`${key}_${values.count === 1 ? "one" : "other"}`] : undefined;
  const template = plural ?? EN[key] ?? (typeof defaultValue === "string" ? defaultValue : key);
  return template.replace(/{{\s*(\w+)\s*}}/g, (_match, name: string) => {
    const value = String(values[name] ?? "");
    return escape ? value.replace(/[&<>"'/]/g, (char) => ESCAPED[char]) : value;
  });
};
