/**
 * Saving a field's vocabulary and its formatting is one PATCH, not two: the
 * column endpoint takes both together, and two requests meant two revisions
 * of the same column for one edit.
 *
 * The field editor itself is stubbed — what is under test is the diff the
 * modal sends on save, not how the values were typed.
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { FieldDefinition } from "@/lib/validations/layer";

import EditFields from "@/components/modals/EditFields";

const { patchColumnMock, renameColumnMock, addColumnMock, datasetResult, queryablesResult } = vi.hoisted(
  () => ({
    patchColumnMock: vi.fn(),
    renameColumnMock: vi.fn(),
    addColumnMock: vi.fn(),
    // One object each, reused by every call. The modal loads its fields in an
    // effect keyed on the queryables object, so a mock that built a fresh one
    // per render would re-run the effect on its own setState for ever.
    datasetResult: { dataset: { feature_layer_geometry_type: "line" } },
    queryablesResult: {
      queryables: {
        properties: {
          maxspeed: {
            type: "number",
            kind: "number",
            allowed_values: [30, 50],
            allow_other: false,
            display_config: { decimals: 0 },
          },
        },
      },
      mutate: vi.fn(),
    },
  })
);

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: "en" } }),
}));
vi.mock("react-toastify", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("swr", () => ({ default: vi.fn(() => ({})), mutate: vi.fn() }));
vi.mock("@/lib/api/layers", () => ({
  COLLECTIONS_API_BASE_URL: "http://localhost:8100/collections",
  addColumn: addColumnMock,
  deleteColumn: vi.fn(),
  patchColumn: patchColumnMock,
  renameColumn: renameColumnMock,
  updateColumnFormula: vi.fn(),
  useDataset: () => datasetResult,
  useLayerQueryables: () => queryablesResult,
}));

/** Stands in for the real editor: one button that applies the edit under test. */
let edit: (fields: FieldDefinition[]) => FieldDefinition[];
vi.mock("@/components/common/FieldEditor", () => ({
  default: ({
    fields,
    onChange,
  }: {
    fields: FieldDefinition[];
    onChange: (fields: FieldDefinition[]) => void;
  }) => (
    <button type="button" onClick={() => onChange(edit(fields))}>
      apply-edit
    </button>
  ),
}));

const applyEdit = () => fireEvent.click(screen.getByRole("button", { name: "apply-edit" }));
const save = () => fireEvent.click(screen.getByRole("button", { name: "save" }));

describe("EditFields save", () => {
  beforeEach(() => {
    patchColumnMock.mockReset();
    patchColumnMock.mockResolvedValue({});
    renameColumnMock.mockReset();
    renameColumnMock.mockResolvedValue({});
  });

  it("sends a vocabulary and a formatting change as one PATCH", async () => {
    edit = (fields) =>
      fields.map((field) => ({
        ...field,
        allowed_values: [30, 50, 70],
        allow_other: true,
        display_config: { decimals: 2 },
      }));
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);

    applyEdit();
    save();
    await vi.waitFor(() => expect(patchColumnMock).toHaveBeenCalled());

    expect(patchColumnMock).toHaveBeenCalledTimes(1);
    expect(patchColumnMock.mock.calls[0][0]).toBe("layer-1");
    expect(patchColumnMock.mock.calls[0][1]).toBe("maxspeed");
    expect(patchColumnMock.mock.calls[0][2]).toEqual({
      allowed_values: [30, 50, 70],
      allow_other: true,
      display_config: { decimals: 2 },
    });
  });

  it("sends only what changed", async () => {
    edit = (fields) => fields.map((field) => ({ ...field, display_config: { decimals: 3 } }));
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);

    applyEdit();
    save();
    await vi.waitFor(() => expect(patchColumnMock).toHaveBeenCalled());

    expect(patchColumnMock.mock.calls[0][2]).toEqual({ display_config: { decimals: 3 } });
  });

  it("does not PATCH a field nothing changed about", async () => {
    edit = (fields) => fields.map((field) => ({ ...field, name: "speed" }));
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);

    applyEdit();
    save();
    await vi.waitFor(() => expect(renameColumnMock).toHaveBeenCalled());

    expect(patchColumnMock).not.toHaveBeenCalled();
  });
});

describe("EditFields adding a generated field", () => {
  beforeEach(() => {
    addColumnMock.mockReset();
    addColumnMock.mockResolvedValue({});
  });

  it("sends a serial field with its start, and a uuid field without one", async () => {
    edit = (fields) => [
      ...fields,
      {
        id: "new-1",
        name: "vorhaben_id",
        kind: "serial",
        is_computed: false,
        display_config: {},
        start: 1000,
      },
      { id: "new-2", name: "uid", kind: "uuid", is_computed: false, display_config: {} },
    ];
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);

    applyEdit();
    save();
    await vi.waitFor(() => expect(addColumnMock).toHaveBeenCalledTimes(2));

    expect(addColumnMock.mock.calls[0]).toEqual([
      "layer-1",
      { name: "vorhaben_id", kind: "serial", display_config: {}, start: 1000 },
    ]);
    expect(addColumnMock.mock.calls[1]).toEqual([
      "layer-1",
      { name: "uid", kind: "uuid", display_config: {} },
    ]);
  });
});
