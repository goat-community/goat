import { ICON_NAME } from "@p4b/ui/components/Icon";

import type { Space } from "@/lib/validations/content";
import type {
  TemplateBadgeKind,
  TemplateInput,
  TemplateKind,
  TemplateRead,
  TemplateSourceFilter,
  TemplateSourceInfo,
} from "@/lib/validations/template";

/** The hint under an empty template shelf, per source — shared by the Home
 * band and the browser, since both are "there is nothing on this shelf". */
export const TEMPLATE_EMPTY_HINT_KEY: Record<TemplateSourceFilter, string> = {
  all: "empty_templates_all",
  // The GOAT shelf holds what GOAT ships, so its hint says what will appear
  // rather than pointing at the catalog the reader is already looking at.
  goat: "templates_empty_goat_hint",
  mine: "empty_templates_mine",
  team: "empty_templates_team",
  org: "empty_templates_org",
  shared: "empty_templates_shared",
};

const SCOPE_LABEL_KEY: Record<TemplateSourceFilter, string> = {
  all: "source_everyone",
  goat: "source_goat",
  mine: "source_mine",
  team: "source_team",
  org: "source_organization",
  shared: "shared_with_me",
};

/** The title an empty template shelf reads as: the unscoped "No templates
 * yet" for Everyone, and the scoped sentence naming the source segment
 * otherwise ("No templates in Mine yet") — one sentence per case rather than
 * a word interpolated in front of "templates", which no language renders
 * naturally. */
export const templateEmptyTitle = (
  t: (key: string, vars?: Record<string, unknown>) => string,
  source: TemplateSourceFilter
): string =>
  source === "all"
    ? t("no_templates_yet_title")
    : t("no_templates_in_scope_title", { scope: t(SCOPE_LABEL_KEY[source]) });

/** The whole-shelf hint the browser dialog shows: the same sentence as the
 * "Mine" shelf's hint, which is the one string that already says how a
 * template gets here. */
export const TEMPLATES_EMPTY_SHELF_HINT_KEY = "empty_templates_mine";

/** What the browser dialog's empty state reads as, in the three ways a list
 * comes back empty: a search or category filter matched nothing, a source
 * narrower than Everyone holds nothing, or the shelf itself is empty. The
 * dialog has no action buttons under it — every filter it names is one click
 * away in the row above the list. */
export const templateBrowserEmptyCopy = (
  filtered: boolean,
  source: TemplateSourceFilter,
  sourceLabel: string
): { titleKey: string; titleVars?: Record<string, string>; hintKey: string } => {
  if (filtered) {
    return { titleKey: "templates_empty_filter_title", hintKey: "templates_empty_filter_hint" };
  }
  if (source !== "all") {
    return {
      titleKey: "templates_empty_source_title",
      titleVars: { source: sourceLabel },
      hintKey: "templates_empty_source_hint",
    };
  }
  return { titleKey: "no_templates_yet_title", hintKey: TEMPLATES_EMPTY_SHELF_HINT_KEY };
};

/** Which shelf a template sits on, as the browser groups and tags them.
 * They mirror the `source` filters `crud_template.list_templates` answers
 * (`goat|mine|team|org|shared`), so a row's tag says the same thing the
 * segment that would return it does. A template shared with one of the
 * caller's teams or with their organization sits on that space's shelf;
 * `shared` is one shared with the caller alone. */
export type TemplateSourceKey = "goat" | "mine" | "team" | "org" | "shared";

/** The order the shelves are stacked in under the "Everyone" segment: the
 * GOAT shelf first, then the caller's own shelves widening outwards, then
 * what others shared with them. */
export const TEMPLATE_SOURCE_ORDER: TemplateSourceKey[] = ["goat", "mine", "team", "org", "shared"];

/** One shelf in the browser's list. GOAT, Mine and Shared are one shelf
 * each, while every team and organization space is its own shelf — a caller
 * in two teams has two team shelves, each named after its own space. */
export interface TemplateShelf {
  /** Identity of the shelf: the source key for GOAT, Mine and Shared, the
   * space id for a team or organization shelf. */
  key: string;
  source: TemplateSourceKey;
  /** The space the shelf is, on team and organization shelves. */
  space?: Space;
}

/**
 * The one source a template is shown under, resolved the way
 * `crud_template.list_templates` resolves its `source` filters: `goat` is
 * `catalog_status = 'published'`, `mine` is the caller's personal spaces,
 * and `team`/`org` are the kind of the space the template lives in — never
 * who created it, which the backend does not look at. The filters overlap
 * (a published template in the caller's own space answers both `goat` and
 * `mine`), so a browser that groups rows takes the published shelf first.
 *
 * `spaces` are the caller's own spaces (`useSpaces`). A template in a space
 * that is not among them, most often someone else's personal space reached
 * through a shared folder, is shelved by `shared_into_space_id`: the team or
 * organization space it was shared into, as the backend's `team`/`org`
 * filters list it. Without one it was shared with the caller alone: `shared`.
 */
/** The caller's space a template is shelved under: the one it lives in, or
 * the team or organization space it was shared into. */
const shelfSpaceOf = (template: TemplateRead, spaces: Space[]): Space | undefined => {
  const spaceId = template.shared_into_space_id ?? template.space_id;
  return spaces.find((entry) => entry.id === spaceId);
};

export const templateSourceOf = (template: TemplateRead, spaces: Space[]): TemplateSourceKey => {
  if (template.catalog_status === "published") return "goat";
  const space = shelfSpaceOf(template, spaces);
  if (!space) return "shared";
  if (space.kind === "team") return "team";
  if (space.kind === "organization") return "org";
  return "mine";
};

/** The shelf a template is grouped and tagged under: its source, plus the
 * space that source came from on a team or organization shelf. */
export const templateShelfOf = (template: TemplateRead, spaces: Space[]): TemplateShelf => {
  const source = templateSourceOf(template, spaces);
  if (source === "goat" || source === "mine" || source === "shared") return { key: source, source };
  const space = shelfSpaceOf(template, spaces);
  return { key: space?.id ?? source, source, space };
};

/** What a shelf is called on a group label or a row tag: GOAT and Mine keep
 * the segment's own wording, while a team or organization shelf is named
 * after its own space — "Marketing" says more than "Team". */
export const templateSourceLabel = (shelf: TemplateShelf, t: (key: string) => string): string => {
  if (shelf.space) return shelf.space.name;
  if (shelf.source === "goat") return t("source_goat");
  if (shelf.source === "mine") return t("source_mine");
  if (shelf.source === "shared") return t("shared_with_me");
  return t(shelf.source === "team" ? "source_team" : "source_organization");
};

/** The order the shelves stack under "Everyone": GOAT, then Mine, then one
 * shelf per team by name, then the organization, then Shared with me. */
export const compareTemplateShelves = (a: TemplateShelf, b: TemplateShelf): number =>
  TEMPLATE_SOURCE_ORDER.indexOf(a.source) - TEMPLATE_SOURCE_ORDER.indexOf(b.source) ||
  (a.space?.name ?? "").localeCompare(b.space?.name ?? "");

/** The source choices a caller has: Everyone, GOAT and Mine always, Team
 * only once they are in a team space, Organization only once an organization
 * space exists, Shared with me once either does — one list, so the inline segments and the dialog's filter
 * popover offer exactly the same choices, and a personal-only account never
 * sees a source it has nothing behind. */
export const templateSourceOptions = (
  spaces: Space[]
): { value: TemplateSourceFilter; labelKey: string }[] => [
  { value: "all", labelKey: "source_everyone" },
  { value: "goat", labelKey: "source_goat" },
  { value: "mine", labelKey: "source_mine" },
  ...(spaces.some((space) => space.kind === "team")
    ? [{ value: "team" as const, labelKey: "source_team" }]
    : []),
  ...(spaces.some((space) => space.kind === "organization")
    ? [{ value: "org" as const, labelKey: "source_organization" }]
    : []),
  // Sharing stays inside an organization, so only a caller in a team or an
  // organization can have anything shared with them alone.
  ...(spaces.some((space) => space.kind === "team" || space.kind === "organization")
    ? [{ value: "shared" as const, labelKey: "shared_with_me" }]
    : []),
];

/** The browser dialog's title: one sentence per locked kind rather than a
 * kind interpolated into a shared one — the noun is capitalised in English
 * and carries gender in German, neither of which survives interpolation. */
export const templateBrowserTitleKey = (lockedKind: TemplateKind | undefined): string =>
  lockedKind ? `new_${lockedKind}_from_template` : "templates";

/** The glyph a template kind or badge is marked with, wherever it is marked —
 * the badges over a card's thumbnail and the tile leading a browser row. */
export const TEMPLATE_KIND_ICON: Record<TemplateBadgeKind, ICON_NAME> = {
  project: ICON_NAME.MAP,
  dashboard: ICON_NAME.CHART,
  workflow: ICON_NAME.WORKFLOW,
  layout: ICON_NAME.REPORT,
};

/** The glyph for a template as a whole: its first kind, falling back to what
 * its payload actually is for a template whose kinds could not be derived. */
export const templateMarkIcon = (template: TemplateRead): ICON_NAME => {
  const kind = (template.kinds ?? [])[0];
  if (kind) return TEMPLATE_KIND_ICON[kind];
  if (template.payload_kind === "workflow") return ICON_NAME.WORKFLOW;
  if (template.payload_kind === "layout") return ICON_NAME.REPORT;
  return ICON_NAME.MAP;
};

/**
 * A template description as one line of plain text: the markdown syntax
 * removed, the words kept. Descriptions are authored and rendered as
 * markdown, so a row or card that clamps one to a couple of lines would
 * otherwise show the author's `##` and `**` marks as text.
 */
export const stripMarkdown = (value: string): string =>
  value
    // A fenced block's fence and its language tag are syntax; the code
    // inside it reads as text.
    .replace(/^[ \t]*(?:```|~~~).*$/gm, " ")
    // An image is not text at all, while a link keeps the label it names.
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/<((?:https?|mailto):[^\s>]+)>/g, "$1")
    // Inline HTML a markdown renderer would have swallowed.
    .replace(/<\/?[a-zA-Z][^>]*>/g, " ")
    // A rule is a line of punctuation with nothing to say.
    .replace(/^[ \t]*(?:[-*_][ \t]*){3,}$/gm, " ")
    // Heading hashes, blockquote marks and list bullets lead their line.
    .replace(/^[ \t]*(?:#{1,6}|>+|[-*+]|\d+[.)])[ \t]+/gm, "")
    // Table pipes and the row of dashes under a header.
    .replace(/^[ \t]*\|?[ \t]*:?-{3,}:?[ \t]*(?:\|[ \t]*:?-{3,}:?[ \t]*)*\|?[ \t]*$/gm, " ")
    .replace(/\|/g, " ")
    // Emphasis, strong and strikethrough marks around their own text. The
    // underscore pair is bounded by non-word characters so `layer_id`
    // survives.
    .replace(/(\*\*|__)([^*_]+)\1/g, "$2")
    .replace(/~~([^~]+)~~/g, "$1")
    .replace(/\*([^*\n]+)\*/g, "$1")
    .replace(/(^|\W)_([^_\n]+)_(?=\W|$)/g, "$1$2")
    // Inline code ticks.
    .replace(/`/g, "")
    .replace(/\s+/g, " ")
    .trim();

/** Links into the project a template was saved from: the project itself,
 * and the project opened on the workflow or layout — the map page's
 * `?workflow=` / `?layout=` intents select the item, and `?mode=` switches
 * to the panel that shows it (`useMapUrlIntent`). */
export const sourceLink = (source: TemplateSourceInfo): { project: string; payload: string | null } => {
  const project = `/map/${source.project_id}`;
  if (source.kind === "workflow" && source.workflow_id) {
    return { project, payload: `${project}?mode=workflows&workflow=${source.workflow_id}` };
  }
  if (source.kind === "layout" && source.layout_id) {
    return { project, payload: `${project}?mode=reports&layout=${source.layout_id}` };
  }
  return { project, payload: null };
};

/** Whether an input keeps the author's dataset: shipped, or copied for each
 * user from it. Either way every user of the template has to be able to read
 * that dataset (`DATASET_MODES` in `core.schemas.template`). */
export const bindsDataset = (input: Pick<TemplateInput, "mode">): boolean =>
  input.mode === "ship" || input.mode === "copy";

/** The author's choice for one dataset in the save dialog: the stored `mode`,
 * with a copy split into "with its rows" and "empty". */
export type TemplateInputChoice = "ship" | "ask" | "copy" | "copy_empty";

/** The dialog's choice for a stored input. */
export const inputChoiceOf = (input: Pick<TemplateInput, "mode" | "copy_content">): TemplateInputChoice =>
  input.mode === "copy" ? (input.copy_content === false ? "copy_empty" : "copy") : input.mode;

/** The stored `mode`/`copy_content` for a dialog choice. */
export const inputFieldsOf = (choice: TemplateInputChoice): Pick<TemplateInput, "mode" | "copy_content"> =>
  choice === "copy_empty"
    ? { mode: "copy", copy_content: false }
    : choice === "copy"
      ? { mode: "copy", copy_content: true }
      : { mode: choice, copy_content: true };

/** The label of each dialog choice. */
export const INPUT_CHOICE_LABEL_KEY: Record<TemplateInputChoice, string> = {
  ship: "template_dataset_ship",
  ask: "ask_on_use",
  copy: "template_dataset_copy",
  copy_empty: "template_dataset_copy_empty",
};

/** A copy needs rows in a table GOAT holds: a raster has none
 * (`crud_template._assert_copy_inputs_copyable`). */
export const canCopyInput = (input: Pick<TemplateInput, "layer_id" | "layer_type">): boolean =>
  !!input.layer_id && input.layer_type !== "raster";

/** Inputs that publishing to the GOAT catalog makes public: the shipped or
 * copied datasets that are neither catalog datasets nor public yet. The
 * backend flips the ones the publisher may share and refuses the rest by
 * name (`crud_template.publish`). */
export const publicOnPublishInputs = (inputs: TemplateInput[]): TemplateInput[] =>
  inputs.filter(
    (input) => bindsDataset(input) && !!input.layer_id && !input.public_read && !input.from_catalog
  );
