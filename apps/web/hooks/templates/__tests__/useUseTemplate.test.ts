/**
 * `templateResultHref` is the whole contract between "Use template" and the
 * map page: it must emit the `?mode=`/`?workflow=`/`?layout=` query params
 * that `useMapUrlIntent` (hooks/map/useMapUrlIntent.ts) reads on mount.
 */
import { mutate } from "swr";
import { describe, expect, it, vi } from "vitest";

import { PROJECTS_API_BASE_URL } from "@/lib/api/projects";
import type { TemplateRead, TemplateUseResult } from "@/lib/validations/template";

import {
  refreshTemplateProject,
  startedCopyJobIds,
  templateResultHref,
} from "@/hooks/templates/useUseTemplate";

vi.mock("swr", async (importOriginal) => ({
  ...(await importOriginal<typeof import("swr")>()),
  mutate: vi.fn(),
}));

const template = {} as TemplateRead;

const baseResult: TemplateUseResult = {
  project_id: "11111111-1111-1111-1111-111111111111",
  workflow_id: null,
  layout_id: null,
  added_layer_project_ids: [],
  unresolved_inputs: [],
  copy_jobs: [],
};

describe("templateResultHref", () => {
  it("opens the workflows panel on the created workflow for a workflow payload", () => {
    const result: TemplateUseResult = { ...baseResult, workflow_id: "22222222-2222-2222-2222-222222222222" };
    expect(templateResultHref(template, result)).toBe(
      "/map/11111111-1111-1111-1111-111111111111?mode=workflows&workflow=22222222-2222-2222-2222-222222222222"
    );
  });

  it("opens the reports panel on the created layout for a layout payload", () => {
    const result: TemplateUseResult = { ...baseResult, layout_id: "33333333-3333-3333-3333-333333333333" };
    expect(templateResultHref(template, result)).toBe(
      "/map/11111111-1111-1111-1111-111111111111?mode=reports&layout=33333333-3333-3333-3333-333333333333"
    );
  });

  it("lands on the plain project route for a project payload (no workflow/layout id)", () => {
    expect(templateResultHref(template, baseResult)).toBe("/map/11111111-1111-1111-1111-111111111111");
  });
});

describe("startedCopyJobIds", () => {
  const job = {
    key: "layer:a",
    source_layer_id: "44444444-4444-4444-4444-444444444444",
    layer_project_ids: [7],
    copy_content: true,
  };

  it("follows only the copy jobs that started", () => {
    const result: TemplateUseResult = {
      ...baseResult,
      copy_jobs: [
        { ...job, job_id: "job-1", error: null },
        { ...job, key: "layer:b", job_id: null, error: "copy_not_started" },
        { ...job, key: "layer:c", job_id: null, error: "source_not_readable" },
      ],
    };
    expect(startedCopyJobIds(result)).toEqual(["job-1"]);
  });

  it("follows nothing for a template without copies", () => {
    expect(startedCopyJobIds(baseResult)).toEqual([]);
  });
});

describe("refreshTemplateProject", () => {
  it("reloads the layers and groups of the project the template was used in", async () => {
    // The layer tree beside "New workflow from a template" reads these keys,
    // so the entries the template added show without a reload.
    await refreshTemplateProject(baseResult);
    expect(mutate).toHaveBeenCalledWith([`${PROJECTS_API_BASE_URL}/${baseResult.project_id}/layer`]);
    expect(mutate).toHaveBeenCalledWith([`${PROJECTS_API_BASE_URL}/${baseResult.project_id}/group`]);
  });
});
