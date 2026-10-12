import { type APIRequestContext, expect } from "@playwright/test";

import { API_URL } from "./users";

/**
 * Templates as the API sees them: the steps of the template specs that are
 * set-up or checks rather than what the spec is about.
 */

export type TemplateInputRead = {
  key: string;
  label: string;
  mode: "ship" | "ask" | "copy";
  copy_content: boolean;
  layer_id: string | null;
};

export type TemplateRead = {
  id: string;
  name: string;
  payload_kind: "workflow" | "layout" | "project";
  inputs: TemplateInputRead[];
  my_role: "owner" | "editor" | "viewer";
};

export type TemplateUseResult = {
  project_id: string;
  workflow_id: string | null;
  added_layer_project_ids: number[];
  copy_jobs: {
    key: string;
    source_layer_id: string;
    layer_project_ids: number[];
    copy_content: boolean;
    job_id: string | null;
    error: "source_not_readable" | "copy_not_started" | null;
  }[];
};

/** The caller's readable template with exactly this name, or undefined. */
export const templateByName = async (
  api: APIRequestContext,
  name: string
): Promise<TemplateRead | undefined> => {
  const listed = await api.get(`${API_URL}/api/v2/template`, { params: { search: name, size: 50 } });
  expect(listed.ok(), await listed.text()).toBeTruthy();
  return ((await listed.json()) as { items: TemplateRead[] }).items.find((item) => item.name === name);
};

/** Grants a role on a template ("template-viewer" / "template-editor"):
 * the same call the Share dialog makes for a template. */
export const grantTemplate = async (
  api: APIRequestContext,
  templateId: string,
  grantee: { type: "user" | "team" | "organization"; id: string },
  role: "template-viewer" | "template-editor" = "template-viewer"
): Promise<void> => {
  const granted = await api.post(`${API_URL}/api/v2/template/${templateId}/grant`, {
    data: { grantee_type: grantee.type, grantee_id: grantee.id, role },
  });
  expect(granted.ok(), await granted.text()).toBeTruthy();
};

/** The template's grants, as the Share dialog lists them. */
export const templateGrants = async (
  api: APIRequestContext,
  templateId: string
): Promise<{ grantee_type: string; grantee_id: string; role: string }[]> => {
  const listed = await api.get(`${API_URL}/api/v2/template/${templateId}/grant`);
  expect(listed.ok(), await listed.text()).toBeTruthy();
  return ((await listed.json()) as { grants: { grantee_type: string; grantee_id: string; role: string }[] })
    .grants;
};

/** `POST /template/{id}/use`: into an existing project or as a new one in
 * a folder. */
export const applyTemplate = async (
  api: APIRequestContext,
  templateId: string,
  body: { project_id?: string; target_folder_id?: string; name?: string }
): Promise<TemplateUseResult> => {
  const used = await api.post(`${API_URL}/api/v2/template/${templateId}/use`, { data: body });
  expect(used.ok(), await used.text()).toBeTruthy();
  return (await used.json()) as TemplateUseResult;
};

/** Deletes a template (its frozen project copy goes to the trash with it).
 * Never fails: cleanup only. */
export const deleteTemplate = async (
  api: APIRequestContext,
  templateId: string | undefined
): Promise<void> => {
  if (templateId) await api.delete(`${API_URL}/api/v2/template/${templateId}`).catch(() => undefined);
};
