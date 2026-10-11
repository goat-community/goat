import { describe, expect, it } from "vitest";

import de from "@/i18n/locales/de/common.json";
import en from "@/i18n/locales/en/common.json";

/**
 * The job tray labels a job with `t(job.processID)`, so a process id with no
 * key renders as the raw id — "catalog_materialize - 07:17 PM". Every id a job
 * can carry therefore needs a label in both languages.
 *
 * The list is written out rather than derived: it is the contract between the
 * Python tool registry and these files, and a test here cannot read that.
 */
const JOB_PROCESS_IDS = [
  "bundle_artifact_delete",
  "bundle_import",
  "catalog_materialize",
  "finalize_layer",
  "layer_copy",
  "layer_create",
  "layer_delete",
  "layer_export",
  "layer_import",
  "print_report",
  "project_export",
  "workflow_runner",
];

describe("job labels", () => {
  it.each(JOB_PROCESS_IDS)("%s is named in English", (id) => {
    expect(typeof (en as unknown as Record<string, unknown>)[id]).toBe("string");
  });

  it.each(JOB_PROCESS_IDS)("%s is named in German", (id) => {
    expect(typeof (de as unknown as Record<string, unknown>)[id]).toBe("string");
  });

  it("does not fall back to the raw id for a catalog materialize job", () => {
    expect((en as unknown as Record<string, string>).catalog_materialize).not.toBe("catalog_materialize");
    expect((de as unknown as Record<string, string>).catalog_materialize).not.toBe("catalog_materialize");
  });
});
