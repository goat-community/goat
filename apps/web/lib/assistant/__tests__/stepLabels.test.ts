import type { DynamicToolUIPart } from "ai";
import { describe, expect, it } from "vitest";

import { plainTranslate } from "@/lib/assistant/chips";
import { ARGUMENT_CHARS, clip, layerNames, stepLabel, stepRows } from "@/lib/assistant/stepLabels";

import { enTranslate } from "./enTranslate";

type State = "output-available" | "output-error" | "input-available";

let counter = 0;
const call = (
  toolName: string,
  input: unknown,
  output?: unknown,
  state: State = output === undefined ? "input-available" : "output-available"
): DynamicToolUIPart =>
  ({
    type: "dynamic-tool",
    toolName,
    toolCallId: `c${(counter += 1)}`,
    state,
    input,
    ...(state === "output-available" ? { output } : {}),
    ...(state === "output-error" ? { errorText: "Internal English detail" } : {}),
  }) as DynamicToolUIPart;
const failed = (toolName: string, input: unknown) => call(toolName, input, undefined, "output-error");

const label = (step: DynamicToolUIPart, steps: DynamicToolUIPart[] = [step]) =>
  stepLabel(step, layerNames(steps), enTranslate);

describe("step labels", () => {
  it("name what core_find searched for, and fall back to the plain label", () => {
    expect(label(call("core_find", { query: "bike" }))).toBe("Searched your content for “bike”");
    expect(label(call("core_find", { query: "bike", kind: "any" }))).toBe("Searched your content for “bike”");
    expect(label(call("core_find", { query: "Anna", kind: "workflow" }))).toBe(
      "Searched workflows for “Anna”"
    );
    expect(label(call("core_find", { query: "A3", kind: "layout" }))).toBe("Searched print layouts for “A3”");
    expect(label(call("core_find", { query: "rad", kind: "dataset" }))).toBe("Searched datasets for “rad”");
    expect(label(call("core_find", { query: "rad", kind: "project" }))).toBe("Searched projects for “rad”");
    expect(label(call("core_find", { query: "rad", kind: "nonsense" }))).toBe(
      "Searched your content for “rad”"
    );
    expect(label(call("core_find", {}))).toBe("Searched your content");
    expect(label(call("core_find", { query: "  " }))).toBe("Searched your content");
    expect(label(call("core_find", undefined))).toBe("Searched your content");
  });

  it("name the catalog search words and count the filters that narrow it", () => {
    expect(label(call("catalog_search", { q: "Radverkehr" }))).toBe("Searched the catalog for “Radverkehr”");
    expect(label(call("catalog_search", { q: "Radverkehr", themes: "transportation", year: 2023 }))).toBe(
      "Searched the catalog for “Radverkehr” (filters: 2)"
    );
    expect(label(call("catalog_search", { themes: "transportation" }))).toBe(
      "Searched the catalog (filters: 1)"
    );
    // Ranking, sorting and paging do not narrow the result.
    expect(
      label(call("catalog_search", { bbox_boost: "1,2,3,4", sortby: "-updated", limit: 5, offset: 5 }))
    ).toBe("Searched the catalog");
    expect(label(call("catalog_search", { q: "", themes: null }))).toBe("Searched the catalog");
    // A region counts as a filter; an empty list of regions does not.
    expect(label(call("catalog_search", { q: "rad", nuts: ["DE212"] }))).toBe(
      "Searched the catalog for “rad” (filters: 1)"
    );
    expect(label(call("catalog_search", { q: "rad", nuts: [] }))).toBe("Searched the catalog for “rad”");
  });

  it("name the region a lookup was for", () => {
    expect(label(call("catalog_find_region", { name: "München" }))).toBe("Looked up the region “München”");
    expect(label(call("catalog_find_region", {}))).toBe("Looked up a region");
    expect(label(call("catalog_show_records", { ids: ["a"] }))).toBe("Listed the recommended datasets");
    expect(label(call("project_get_workflows", {}))).toBe("Listed the project's workflows");
    expect(label(call("project_get_workflows", {}, { project_name: "Tool 4 V2", workflows: [] }))).toBe(
      "Listed the workflows of “Tool 4 V2”"
    );
    expect(label(call("project_get_layouts", {}, { project_name: "Tool 3", layouts: [] }))).toBe(
      "Listed the print layouts of “Tool 3”"
    );
    expect(label(call("core_show_items", { groups: [] }))).toBe("Listed the matching items");
  });

  it("name a catalog record by its title, else its id", () => {
    const record = { item_id: "ds-1" };
    expect(label(call("catalog_get_record", record, { title: "Radverkehrsnetz" }))).toBe(
      "Read the catalog record “Radverkehrsnetz”"
    );
    expect(label(call("catalog_get_record", record, { properties: { title: "Item title" } }))).toBe(
      "Read the catalog record “Item title”"
    );
    expect(label(call("catalog_get_record", record))).toBe("Read the catalog record “ds-1”");
    expect(label(call("catalog_get_record", {}))).toBe("Read a catalog record");
  });

  it("name the prefix of a term check, and keep tools without a main argument plain", () => {
    expect(label(call("catalog_suggest_terms", { prefix: "rad" }))).toBe("Checked search terms for “rad”");
    expect(label(call("catalog_describe", { max_values: 5 }, { items: 1 }))).toBe("Read the catalog filters");
    expect(label(call("map_propose_view", { title: "Berlin" }, {}))).toBe("Prepared a map view");
    expect(label(call("core_whoami", {}, {}))).toBe("Read your account");
    expect(label(call("some_new_tool", {}, {}))).toBe("some_new_tool");
  });

  it("name the layer a project tool read from its result", () => {
    const layer = { layer_project_id: 87152 };
    expect(label(call("project_get_fields", layer, { layer: "Radwege" }))).toBe(
      "Read the fields of “Radwege”"
    );
    expect(label(call("project_sample_features", layer, { layer: "Radwege" }))).toBe(
      "Read sample features of “Radwege”"
    );
    expect(label(call("project_area_statistics", layer, { layer: "Radwege" }))).toBe(
      "Computed area statistics of “Radwege”"
    );
    expect(label(call("project_count_features", layer, { layer: "Radwege", count: 4 }))).toBe(
      "Counted features in “Radwege”"
    );
  });

  it("mark a filtered count, and tell two counts of one layer apart", () => {
    const filter = { conditions: [{ field: "surface", op: "=", value: "asphalt" }] };
    const plain = call("project_count_features", { layer_project_id: 1 }, { layer: "Radwege" });
    const filtered = call("project_count_features", { layer_project_id: 1, filter }, { layer: "Radwege" });
    expect(label(plain)).toBe("Counted features in “Radwege”");
    expect(label(filtered)).toBe("Counted features in “Radwege” (filtered)");
    expect(label(call("project_count_features", { layer_project_id: 1, filter: null }, { layer: "A" }))).toBe(
      "Counted features in “A”"
    );
  });

  it("name the field and the layer of a field statistic", () => {
    const step = call(
      "project_field_statistics",
      { layer_project_id: 3, field: "width" },
      { layer: "Radwege" }
    );
    expect(label(step)).toBe("Computed statistics of “width” in “Radwege”");
    expect(label(call("project_field_statistics", { layer_project_id: 3 }, { layer: "Radwege" }))).toBe(
      "Computed field statistics"
    );
  });

  it("name the project of a layer list", () => {
    expect(label(call("project_get_layers", { project_id: "p1" }, { name: "Bike plan", layers: [] }))).toBe(
      "Read the layers of “Bike plan”"
    );
    expect(label(call("project_get_layers", {}))).toBe("Read the project layers");
  });

  it("take a layer's name from the answer's layer list while the call has no result", () => {
    const layers = call(
      "project_get_layers",
      {},
      {
        project_id: "p1",
        name: "Bike plan",
        layers: [
          { layer_project_id: 87152, name: "Radwege" },
          { layer_project_id: 9, name: "Parks" },
        ],
      }
    );
    const running = call("project_count_features", { layer_project_id: 87152 });
    const broken = failed("project_get_fields", { layer_project_id: 9, project_id: "p1" });
    const steps = [layers, running, broken];
    expect(label(running, steps)).toBe("Counted features in “Radwege”");
    expect(label(broken, steps)).toBe("Read the fields of “Parks”");
  });

  it("do not give one project's layer name to another project's layer", () => {
    const layers = call(
      "project_get_layers",
      { project_id: "p1" },
      { project_id: "p1", name: "One", layers: [{ layer_project_id: 5, name: "Radwege" }] }
    );
    const other = call("project_count_features", { layer_project_id: 5, project_id: "p2" });
    const current = call("project_count_features", { layer_project_id: 5 });
    expect(label(other, [layers, other])).toBe("Counted features in layer 5");
    // A call without project_id is about the open project, which this list did not name.
    expect(label(current, [layers, current])).toBe("Counted features in layer 5");
    const same = call("project_count_features", { layer_project_id: 5, project_id: "p1" });
    expect(label(same, [layers, same])).toBe("Counted features in “Radwege”");
  });

  it("fall back to the layer's ID when no name is known", () => {
    expect(label(call("project_count_features", { layer_project_id: 87152 }))).toBe(
      "Counted features in layer 87152"
    );
    expect(label(failed("project_get_fields", { layer_project_id: 87152 }))).toBe(
      "Read the fields of layer 87152"
    );
    expect(
      label(
        call(
          "project_field_statistics",
          { layer_project_id: 87152, field: "width" },
          undefined,
          "output-error"
        )
      )
    ).toBe("Computed statistics of “width” in layer 87152");
    expect(label(call("project_count_features", {}))).toBe("Counted features");
  });

  it("cut a long argument to one line with an ellipsis", () => {
    const long = "Radverkehr ".repeat(20);
    const text = label(call("core_find", { query: `${long}\nmore` }));
    expect(text).not.toMatch(/\n/);
    const argument = text.slice("Searched your content for “".length, -1);
    expect(Array.from(argument)).toHaveLength(ARGUMENT_CHARS);
    expect(argument.endsWith("…")).toBe(true);
    expect(clip("short")).toBe("short");
    expect(clip("a".repeat(ARGUMENT_CHARS))).toBe("a".repeat(ARGUMENT_CHARS));
    expect(clip("a".repeat(ARGUMENT_CHARS + 1))).toBe(`${"a".repeat(ARGUMENT_CHARS - 1)}…`);
    // A character outside the BMP is not cut in half.
    expect(clip("🚲".repeat(ARGUMENT_CHARS + 5))).toBe(`${"🚲".repeat(ARGUMENT_CHARS - 1)}…`);
    // A layer name is cut like any other argument.
    const layer = label(call("project_get_fields", { layer_project_id: 1 }, { layer: "L".repeat(80) }));
    expect(layer).toBe(`Read the fields of “${"L".repeat(ARGUMENT_CHARS - 1)}…”`);
  });

  it("leave the values unescaped for the React text they end up in", () => {
    const step = call("core_find", { query: "a & <b> / 'c'" });
    expect(stepLabel(step, layerNames([step]), plainTranslate(enTranslate))).toBe(
      "Searched your content for “a & <b> / 'c'”"
    );
  });
});

describe("step rows", () => {
  const ids = (steps: DynamicToolUIPart[]) => steps.map((step) => step.toolCallId);
  const shape = (steps: DynamicToolUIPart[]) =>
    stepRows(steps).map((row) => [row.step.toolCallId, ids(row.rejected)]);

  it("folds a rejected attempt into the successful call of the same tool right after it", () => {
    const rejected = failed("project_count_features", { layer_project_id: 1, filter: "bad" });
    const retry = call("project_count_features", { layer_project_id: 1 }, { layer: "A", count: 3 });
    expect(shape([rejected, retry])).toEqual([[retry.toolCallId, [rejected.toolCallId]]]);
  });

  it("folds several rejected attempts into the call that finally succeeded", () => {
    const first = failed("core_find", { query: "" });
    const second = failed("core_find", { query: "x" });
    const ok = call("core_find", { query: "xy" }, { projects: [], datasets: [] });
    expect(shape([first, second, ok])).toEqual([[ok.toolCallId, [first.toolCallId, second.toolCallId]]]);
  });

  it("keeps a failure that no successful retry of the same tool follows", () => {
    const lone = failed("core_find", { query: "x" });
    const other = call("core_whoami", {}, {});
    const last = failed("catalog_search", { q: "a" });
    expect(shape([lone, other, last])).toEqual([
      [lone.toolCallId, []],
      [other.toolCallId, []],
      [last.toolCallId, []],
    ]);
    // A success of another tool in between does not count as the retry.
    const retry = call("core_find", { query: "xy" }, {});
    expect(shape([lone, other, retry])).toEqual([
      [lone.toolCallId, []],
      [other.toolCallId, []],
      [retry.toolCallId, []],
    ]);
    // Neither does a retry that is still running or fails as well.
    const running = call("core_find", { query: "xy" });
    expect(shape([lone, running])).toEqual([
      [lone.toolCallId, []],
      [running.toolCallId, []],
    ]);
    const again = failed("core_find", { query: "xy" });
    expect(shape([lone, again])).toEqual([
      [lone.toolCallId, []],
      [again.toolCallId, []],
    ]);
  });

  it("does not fold a failure into an earlier success, or a success into nothing", () => {
    const ok = call("core_find", { query: "x" }, {});
    const bad = failed("core_find", { query: "y" });
    expect(shape([ok, bad])).toEqual([
      [ok.toolCallId, []],
      [bad.toolCallId, []],
    ]);
  });
});
