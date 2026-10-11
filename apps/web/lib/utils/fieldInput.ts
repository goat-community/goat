/**
 * Shared helpers for editing field values by kind. Every editor surface
 * (feature panel, data table cells, map edit popover) goes through these so
 * option labels, parsing, and serialization stay identical.
 */

/** Options for boolean value dropdowns; the empty option writes NULL. */
export const BOOLEAN_SELECT_ITEMS = [
  { value: "", label: "—" },
  { value: "true", label: "True" },
  { value: "false", label: "False" },
] as const;

/** {@link BOOLEAN_SELECT_ITEMS} with the true/false labels in the reader's language. */
export const getBooleanSelectItems = (t: (key: string) => string) =>
  BOOLEAN_SELECT_ITEMS.map((item) =>
    item.value === "" ? item : { ...item, label: t(item.value === "true" ? "boolean_true" : "boolean_false") }
  );

/** Select-input string -> stored boolean value ("" -> NULL). */
export const parseBooleanInput = (value: string): boolean | null =>
  value === "" ? null : value === "true";

/** Stored boolean value -> select-input string (NULL/undefined -> ""). */
export const booleanToSelectValue = (raw: unknown): string =>
  raw === true ? "true" : raw === false ? "false" : "";
