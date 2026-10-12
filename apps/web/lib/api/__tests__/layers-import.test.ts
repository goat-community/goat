import { beforeEach, describe, expect, it, vi } from "vitest";

import { createLayer } from "@/lib/api/layers";

const { executeMock } = vi.hoisted(() => ({ executeMock: vi.fn() }));
vi.mock("@/lib/api/fetcher", () => ({ apiRequestAuth: vi.fn(), fetcher: vi.fn() }));
vi.mock("@/lib/api/processes", () => ({ executeProcessAsync: executeMock }));
vi.mock("swr", () => ({ default: vi.fn(() => ({})), mutate: vi.fn() }));

describe("createLayer", () => {
  beforeEach(() => {
    executeMock.mockReset();
    executeMock.mockResolvedValue({ jobID: "job-1" });
  });

  it("starts the import with the upload, the folder and the name, and no layer id", async () => {
    // processes refuses any layer id the caller cannot read, and a layer
    // that does not exist yet is one: sending one failed every upload.
    await createLayer({
      name: "Roads",
      folder_id: "folder-1",
      s3_key: "goat/users/u/imports/uploads/roads.gpkg",
      public_read: false,
    });

    expect(executeMock).toHaveBeenCalledWith("layer_import", {
      name: "Roads",
      folder_id: "folder-1",
      s3_key: "goat/users/u/imports/uploads/roads.gpkg",
    });
  });
});
