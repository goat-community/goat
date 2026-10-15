import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

import de from "@/i18n/locales/de/common.json";
import en from "@/i18n/locales/en/common.json";

import { RUN_ERROR_CODES } from "@/lib/assistant/types";

const EN = en as unknown as Record<string, string>;
const DE = de as unknown as Record<string, string>;
const assistantKeys = (texts: Record<string, string>) =>
  Object.keys(texts)
    .filter((k) => k.startsWith("assistant_"))
    .sort();

const TOOLS = [
  "core_find",
  "core_page_context",
  "core_whoami",
  "catalog_describe",
  "catalog_get_record",
  "catalog_propose_filters",
  "catalog_search",
  "catalog_suggest_terms",
  "map_propose_view",
  "project_area_statistics",
  "project_count_features",
  "project_field_statistics",
  "project_get_fields",
  "project_get_layers",
  "project_sample_features",
];
const ROWS = [
  "q",
  "themes",
  "license",
  "language",
  "publisher",
  "type",
  "geometry_type",
  "geographical_code",
  "year",
  "from",
  "to",
  "nuts",
  "sortby",
  "number_matched",
  "project",
  "center",
  "zoom",
  "bbox",
  "layer",
  "filter",
];
const GROUPS = ["catalog", "project", "none"];

/** Every literal `assistant_…` key in the dock's source files. */
function usedKeys(): string[] {
  const roots = ["components/assistant", "lib/assistant", "hooks/assistant"].map((dir) =>
    path.join(__dirname, "../..", dir)
  );
  const files: string[] = [];
  const walk = (dir: string) => {
    for (const name of readdirSync(dir)) {
      const full = path.join(dir, name);
      if (statSync(full).isDirectory()) {
        if (name !== "__tests__") walk(full);
      } else if (/\.tsx?$/.test(name)) files.push(full);
    }
  };
  roots.forEach((root) => {
    try {
      walk(root);
    } catch (error) {
      // a root created by a later task may not exist yet
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
    }
  });
  const keys = new Set<string>();
  for (const file of files) {
    for (const match of readFileSync(file, "utf8").matchAll(/["'](assistant_[a-z0-9_]+)["']/g))
      keys.add(match[1]);
  }
  return [...keys].sort();
}

describe("assistant texts", () => {
  it("exist in English and German with the same keys and placeholders", () => {
    expect(assistantKeys(DE)).toEqual(assistantKeys(EN));
    for (const key of assistantKeys(EN)) {
      const placeholders = (text: string) => [...text.matchAll(/{{\s*(\w+)\s*}}/g)].map((m) => m[1]).sort();
      expect(placeholders(DE[key]), key).toEqual(placeholders(EN[key]));
    }
  });

  it("use no dashes inside sentences", () => {
    for (const key of assistantKeys(EN)) {
      expect(EN[key], key).not.toMatch(/[—–]/);
      expect(DE[key], key).not.toMatch(/[—–]/);
    }
  });

  it("cover every key the dock uses, and the dynamic families", () => {
    expect(usedKeys().length).toBeGreaterThan(0);
    const missing = usedKeys().filter((key) => !(key in EN));
    expect(missing).toEqual([]);
    for (const tool of TOOLS) expect(EN, tool).toHaveProperty(`assistant_tool_${tool}`);
    for (const code of RUN_ERROR_CODES) expect(EN, code).toHaveProperty(`assistant_run_error_${code}`);
    for (const row of ROWS) expect(EN, row).toHaveProperty(`assistant_proposal_row_${row}`);
    for (const group of GROUPS) {
      expect(EN).toHaveProperty(`assistant_empty_heading_${group}`);
      expect(EN).toHaveProperty(`assistant_empty_sub_${group}`);
      for (const n of [1, 2, 3]) expect(EN).toHaveProperty(`assistant_suggestion_${group}_${n}`);
    }
  });
});
