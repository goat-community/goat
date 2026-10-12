/**
 * Turning an existing number column into a serial in "Edit fields": the type
 * selector of an existing number field offers Serial (and back), saving asks
 * for confirmation first, the change travels as its own PATCH, and a refusal
 * from the server (duplicates, fractions) is shown as the server worded it.
 *
 * The field editor itself is stubbed, as in EditFields.patch.test.tsx.
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { FieldDefinition } from "@/lib/validations/layer";

import EditFields from "@/components/modals/EditFields";

const { patchColumnMock, toastError, editorProps, datasetResult, queryablesResult } = vi.hoisted(() => ({
  patchColumnMock: vi.fn(),
  toastError: vi.fn(),
  editorProps: { current: {} as Record<string, unknown> },
  datasetResult: { dataset: { feature_layer_geometry_type: "point" } },
  queryablesResult: {
    queryables: {
      properties: {
        vorhaben_id: { type: "number", kind: "number", display_config: {} },
        titel: { type: "string", kind: "string", display_config: {} },
        lfd_nr: { type: "integer", kind: "serial", start: 1, display_config: {} },
      },
    },
    mutate: vi.fn(),
  },
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => (opts ? `${key}:${JSON.stringify(opts)}` : key),
    i18n: { language: "de" },
  }),
}));
vi.mock("react-toastify", () => ({ toast: { success: vi.fn(), error: toastError } }));
vi.mock("swr", () => ({ default: vi.fn(() => ({})), mutate: vi.fn() }));
vi.mock("@/lib/api/layers", () => ({
  COLLECTIONS_API_BASE_URL: "http://localhost:8100/collections",
  addColumn: vi.fn(),
  deleteColumn: vi.fn(),
  patchColumn: patchColumnMock,
  renameColumn: vi.fn(),
  updateColumnFormula: vi.fn(),
  useDataset: () => datasetResult,
  useLayerQueryables: () => queryablesResult,
}));

let edit: (fields: FieldDefinition[]) => FieldDefinition[];
vi.mock("@/components/common/FieldEditor", () => ({
  default: (props: { fields: FieldDefinition[]; onChange: (fields: FieldDefinition[]) => void }) => {
    editorProps.current = props as unknown as Record<string, unknown>;
    return (
      <button type="button" onClick={() => props.onChange(edit(props.fields))}>
        apply-edit
      </button>
    );
  },
}));

const applyEdit = () => fireEvent.click(screen.getByRole("button", { name: "apply-edit" }));
const save = () => fireEvent.click(screen.getByRole("button", { name: "save" }));
const toSerial = (start?: number) => (fields: FieldDefinition[]) =>
  fields.map((f) => (f.name === "vorhaben_id" ? { ...f, kind: "serial" as const, start } : f));

describe("EditFields kind conversion", () => {
  beforeEach(() => {
    patchColumnMock.mockReset();
    patchColumnMock.mockResolvedValue({});
    toastError.mockReset();
  });

  it("offers number <-> serial on existing number and serial fields only", () => {
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);
    expect(editorProps.current.kindChoicesByField).toEqual({
      vorhaben_id: ["number", "serial"],
      lfd_nr: ["number", "serial"],
    });
  });

  it("asks before converting, then sends the kind change on its own", async () => {
    edit = toSerial(1000);
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);
    applyEdit();
    save();

    // Nothing is sent until the user has read what happens to the values.
    expect(patchColumnMock).not.toHaveBeenCalled();
    expect(screen.getByText(/convert_to_serial_confirm/)).toBeTruthy();
    expect(screen.getByText(/"name":"vorhaben_id"/)).toBeTruthy();
    // The start of an existing column about to become a serial can be set.
    expect([...(editorProps.current.startEditableFieldIds as Set<string>)]).toEqual(["vorhaben_id"]);

    fireEvent.click(screen.getByRole("button", { name: "convert_field" }));
    await vi.waitFor(() => expect(patchColumnMock).toHaveBeenCalled());
    expect(patchColumnMock).toHaveBeenCalledTimes(1);
    expect(patchColumnMock.mock.calls[0]).toEqual([
      "layer-1",
      "vorhaben_id",
      { kind: "serial", start: 1000 },
    ]);
  });

  it("cancelling the confirmation sends nothing", () => {
    edit = toSerial();
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);
    applyEdit();
    save();
    // The confirmation's own cancel, the last one on screen.
    const cancels = screen.getAllByRole("button", { name: "cancel" });
    fireEvent.click(cancels[cancels.length - 1]);
    expect(patchColumnMock).not.toHaveBeenCalled();
  });

  it("shows the server's reason when the conversion is refused", async () => {
    patchColumnMock.mockRejectedValue(
      new Error("'vorhaben_id' cannot become a serial number: some values appear more than once: 5 (2×).")
    );
    edit = toSerial();
    const onClose = vi.fn();
    render(<EditFields open onClose={onClose} layerId="layer-1" />);
    applyEdit();
    save();
    fireEvent.click(screen.getByRole("button", { name: "convert_field" }));
    await vi.waitFor(() => expect(toastError).toHaveBeenCalled());
    const message = String(toastError.mock.calls[0][0]);
    expect(message).toContain("convert_field_failed");
    expect(message).toContain("5 (2×)");
    expect(onClose).not.toHaveBeenCalled();
  });

  it("converts a serial back to a number", async () => {
    edit = (fields) => fields.map((f) => (f.name === "lfd_nr" ? { ...f, kind: "number" as const } : f));
    render(<EditFields open onClose={() => {}} layerId="layer-1" />);
    applyEdit();
    save();
    expect(screen.getByText(/convert_to_number_confirm/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "convert_field" }));
    await vi.waitFor(() => expect(patchColumnMock).toHaveBeenCalled());
    expect(patchColumnMock.mock.calls[0]).toEqual(["layer-1", "lfd_nr", { kind: "number" }]);
  });
});
