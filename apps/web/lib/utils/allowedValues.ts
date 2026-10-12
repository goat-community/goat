import { isGeneratedKind } from "@/lib/validations/layer";

import type { SelectorItem } from "@/types/map/common";

/** A column constrained to a vocabulary, as the field metadata reports it. */
export type VocabularyField = {
  allowed_values?: (string | number)[];
  allow_other?: boolean;
  default_value?: unknown;
};

/** Whether a field carries a vocabulary at all. */
function hasVocabulary(field: VocabularyField): boolean {
  return Array.isArray(field.allowed_values) && field.allowed_values.length > 0;
}

/**
 * The options to offer for a constrained column, given what it holds now.
 *
 * A value already in the data that is outside the vocabulary is included, so
 * editing some other attribute of that feature does not quietly rewrite this
 * one — imported data predates the vocabulary and legitimately holds values it
 * does not contain. Only what the user may newly choose is constrained.
 *
 * An empty option leads when the column has no default, because a constrained
 * column is not thereby a required one and clearing it has to stay possible.
 * With a default it is left out: the value would come straight back — a street
 * network edge's class is refilled on every save, so offering a blank would
 * show the user a choice that silently undoes itself.
 */
export function vocabularyItems(field: VocabularyField, current: unknown): SelectorItem[] {
  const allowed = field.allowed_values ?? [];
  const clearable = field.default_value === undefined || field.default_value === null;
  const items: SelectorItem[] = [
    ...(clearable ? [{ value: "", label: "—" }] : []),
    ...allowed.map((value) => ({ value, label: String(value) })),
  ];
  const isSet = current !== null && current !== undefined && current !== "";
  if (isSet && !allowed.some((value) => String(value) === String(current))) {
    items.push({ value: current as string | number, label: String(current) });
  }
  return items;
}

/** The item matching a stored value, for Selector's controlled `selectedItems`. */
export function selectedVocabularyItem(items: SelectorItem[], current: unknown): SelectorItem | undefined {
  if (current === null || current === undefined || current === "") return undefined;
  return items.find((item) => String(item.value) === String(current));
}

/** A column's editing metadata, as the field metadata reports it. */
export type EditableField = VocabularyField & {
  kind?: string;
  is_computed?: boolean;
  is_locked?: boolean;
  is_generated?: boolean;
};

/**
 * How one column may be edited.
 *
 * The single derivation for every editing surface — the attribute panel, the
 * map's popover editor and the data table — so a column cannot be typed into
 * in one and picked from in another.
 */
export type FieldEditability = {
  /** Derived from other columns, and recomputed on save. */
  computed: boolean;
  /** Maintained by whatever owns the layer — a street network's endpoints are
   *  resolved against its nodes on every save. Not derived: there is no
   *  formula and nothing to recompute. */
  locked: boolean;
  /** Assigned by the server when the feature is created — a serial number or a
   *  UUID — and never changed afterwards. Blank until the feature is saved. */
  generated: boolean;
  /** Shown but never edited, for any of these reasons. */
  readOnly: boolean;
  /** Edited by picking: the vocabulary is the whole set of accepted values. */
  vocabulary: boolean;
  /** Edited by typing, with the vocabulary offered as suggestions only. */
  suggestions: boolean;
  /** What to offer; empty unless `vocabulary` or `suggestions`. */
  items: SelectorItem[];
};

export function fieldEditability(field: EditableField, current?: unknown): FieldEditability {
  const computed = field.is_computed === true;
  const locked = field.is_locked === true;
  // The flag is what the server reports; the kind covers field metadata built
  // before the flag existed (and the create dialog, which has no server yet).
  const generated = field.is_generated === true || isGeneratedKind(field.kind);
  const readOnly = computed || locked || generated;
  const constrained = !readOnly && hasVocabulary(field);
  // "Allow other values" makes the vocabulary a set of suggestions rather than
  // the domain: the backend accepts a value outside it, so the editor has to
  // let one be entered.
  const suggestions = constrained && field.allow_other === true;
  return {
    computed,
    locked,
    generated,
    readOnly,
    vocabulary: constrained && !suggestions,
    suggestions,
    items: constrained ? vocabularyItems(field, current) : [],
  };
}

/** A field that supplies a value when a new feature leaves it blank. */
export type DefaultedField = { name: string; default_value?: unknown };

/**
 * The properties a newly created feature starts with.
 *
 * Seeded in the editor rather than left to the server so the user sees the
 * value that will be stored. The write path applies the same defaults, so an
 * API caller gets them too — this only decides what is on screen.
 */
export function defaultProperties(fields: DefaultedField[]): Record<string, unknown> {
  const seeded: Record<string, unknown> = {};
  for (const field of fields) {
    if (field.default_value !== undefined && field.default_value !== null) {
      seeded[field.name] = field.default_value;
    }
  }
  return seeded;
}
