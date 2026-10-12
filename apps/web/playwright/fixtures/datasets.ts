import { type APIRequestContext, expect, request } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

import { API_URL, castOf } from "./users";

/**
 * Datasets as the API sees them: the suite's checks that an upload became a
 * real layer, with its rows in DuckLake and served by geoapi.
 */

export const GEOAPI_URL = process.env.NEXT_PUBLIC_GEOAPI_URL ?? "http://127.0.0.1:8100";

/** The id of the caller's dataset with exactly this name, or undefined. */
export const datasetIdByName = async (api: APIRequestContext, name: string): Promise<string | undefined> => {
  const response = await api.post(`${API_URL}/api/v2/layer`, { data: { search: name } });
  expect(response.status()).toBe(200);
  const { items } = (await response.json()) as { items: { id: string; name: string }[] };
  return items.find((item) => item.name === name)?.id;
};

/** How many rows geoapi serves for a dataset. */
export const rowCount = async (api: APIRequestContext, layerId: string): Promise<number> => {
  const response = await api.get(`${GEOAPI_URL}/collections/${layerId}/items?limit=1`);
  expect(response.status(), await response.text()).toBe(200);
  return ((await response.json()) as { numberMatched: number }).numberMatched;
};

/** The id of one of the owner's provisioned datasets (auth on only). */
export const datasetOf = (key: "points" | "table" | "editable"): string => castOf().datasets[key];

/** Shares a dataset with users ("layer-viewer" / "layer-editor"). */
export const shareDatasetWithUsers = async (
  api: APIRequestContext,
  layerId: string,
  users: { id: string; role: "layer-viewer" | "layer-editor" }[]
): Promise<void> => {
  const shared = await api.post(`${API_URL}/api/v2/share/layer/${layerId}`, { data: { users } });
  expect(shared.ok(), await shared.text()).toBeTruthy();
};

export const PROCESSES_URL = process.env.NEXT_PUBLIC_PROCESSES_URL ?? "http://127.0.0.1:8300";

/** Waits for a processes job to leave accepted/running and returns its
 * final status record. */
export const waitForJob = async (
  api: APIRequestContext,
  jobId: string,
  timeout = 300000
): Promise<{ status: string; message?: string }> => {
  let job: { status: string; message?: string } = { status: "accepted" };
  await expect
    .poll(
      async () => {
        const response = await api.get(`${PROCESSES_URL}/jobs/${jobId}`);
        expect(response.ok(), await response.text()).toBeTruthy();
        job = (await response.json()) as { status: string; message?: string };
        return job.status;
      },
      { timeout, intervals: [1000, 2000, 3000] }
    )
    .not.toMatch(/^(accepted|running)$/);
  return job;
};

/**
 * Uploads a file as a new dataset of the caller, the way the app and
 * `scripts/e2e/provision.py` do (a presigned PUT, then the `layer_import`
 * job, which needs Windmill), into the caller's home folder unless a folder
 * is given. Returns the new dataset's id.
 */
export const uploadDataset = async (
  api: APIRequestContext,
  name: string,
  file: { path: string; contentType: string },
  folderId?: string
): Promise<string> => {
  const body = fs.readFileSync(file.path);
  const presigned = await api.post(`${API_URL}/api/v2/datasets/request-upload`, {
    data: { filename: path.basename(file.path), content_type: file.contentType, file_size: body.length },
  });
  expect(presigned.ok(), await presigned.text()).toBeTruthy();
  const upload = (await presigned.json()) as { url: string; key: string; headers: Record<string, string> };
  // Without the caller's bearer token: the URL carries its own signature,
  // and S3 refuses a request that brings a second one.
  const s3 = await request.newContext();
  try {
    const put = await s3.put(upload.url, { data: body, headers: upload.headers });
    expect(put.ok(), await put.text()).toBeTruthy();
  } finally {
    await s3.dispose();
  }

  let folder = folderId;
  if (!folder) {
    const folders = await api.get(`${API_URL}/api/v2/folder`);
    expect(folders.ok(), await folders.text()).toBeTruthy();
    folder = ((await folders.json()) as { id: string; name: string; is_owned: boolean }[]).find(
      (candidate) => candidate.name === "home" && candidate.is_owned
    )?.id;
    expect(folder, "no owned home folder").toBeTruthy();
  }
  const submitted = await api.post(`${PROCESSES_URL}/processes/layer_import/execution`, {
    data: { inputs: { folder_id: folder, name, s3_key: upload.key } },
  });
  expect(submitted.ok(), await submitted.text()).toBeTruthy();
  const jobId = ((await submitted.json()) as { jobID: string }).jobID;
  const job = await waitForJob(api, jobId);
  expect(job.status, `importing ${name}: ${job.message}`).toBe("successful");
  const results = await api.get(`${PROCESSES_URL}/jobs/${jobId}/results`);
  expect(results.ok(), await results.text()).toBeTruthy();
  const imported = ((await results.json()) as { result?: { imported?: { layer_id: string }[] } }).result
    ?.imported;
  expect(imported, `importing ${name} gave no layer`).toHaveLength(1);
  return imported![0].layer_id;
};

/** The suite's 26 points (`fixtures/data/points.geojson`). */
export const POINTS_FILE = {
  path: path.join(__dirname, "data", "points.geojson"),
  contentType: "application/geo+json",
};

/** Moves a dataset to its owner's trash. Never fails: cleanup only. */
export const deleteDataset = async (api: APIRequestContext, layerId: string | undefined): Promise<void> => {
  if (layerId) await api.delete(`${API_URL}/api/v2/layer/${layerId}`).catch(() => undefined);
};
