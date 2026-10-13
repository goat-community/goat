import { describe, expect, it } from "vitest";

import type { JobType } from "@/lib/api/processes";
import { jobLabel } from "@/lib/utils/jobLabel";

const t = (key: string, vars?: Record<string, unknown>) => (vars ? `${key}:${JSON.stringify(vars)}` : key);

describe("jobLabel", () => {
  it("names a template copy after the entry it is made for", () => {
    expect(jobLabel({ processID: "layer_copy", inputs: { layer_name: "Vorhaben (Eingabe)" } }, t)).toBe(
      `layer_copy_named:${JSON.stringify({ name: "Vorhaben (Eingabe)" })}`
    );
  });

  it("falls back to the tool's label without a name", () => {
    expect(jobLabel({ processID: "layer_copy", inputs: {} }, t)).toBe("layer_copy");
    expect(jobLabel({ processID: "layer_copy", inputs: { layer_name: " " } }, t)).toBe("layer_copy");
    expect(jobLabel({ processID: "layer_copy" }, t)).toBe("layer_copy");
  });

  it("leaves every other job its tool's label", () => {
    expect(jobLabel({ processID: "layer_import", inputs: { layer_name: "x" } }, t)).toBe("layer_import");
  });

  it("shows the raw id rather than nothing for a tool without a label", () => {
    expect(jobLabel({ processID: "mystery" as JobType }, () => "")).toBe("mystery");
  });
});
