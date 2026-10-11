/**
 * The serial and UUID kinds in the field editor: offered in the kind selector
 * — also when a new layer is being created, where computed kinds are not —
 * and a serial's start number is a setting of its own.
 */
import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { FieldDefinition } from "@/lib/validations/layer";

import FieldEditor from "@/components/common/FieldEditor";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => `i18n:${key}`, i18n: { language: "de" } }),
}));

const field = (overrides: Partial<FieldDefinition>): FieldDefinition =>
  ({
    id: "f1",
    name: "vorhaben_id",
    kind: "boolean",
    is_computed: false,
    display_config: {},
    ...overrides,
  }) as FieldDefinition;

const renderEditor = (props: Partial<React.ComponentProps<typeof FieldEditor>> = {}) => {
  const onChange = vi.fn();
  render(
    <FieldEditor
      fields={[field({})]}
      onChange={onChange}
      selectedFieldId="f1"
      onSelectField={() => {}}
      geometryType="point"
      {...props}
    />
  );
  return onChange;
};

const openKindSelector = async () => {
  const user = userEvent.setup();
  await user.click(screen.getByRole("combobox"));
  return screen.findByRole("listbox");
};

describe("FieldEditor generated kinds", () => {
  it("offers serial and UUID when creating a layer, but no computed kinds", async () => {
    renderEditor();
    const list = await openKindSelector();
    expect(within(list).getByText("i18n:field_kind_serial")).toBeTruthy();
    expect(within(list).getByText("i18n:field_kind_uuid")).toBeTruthy();
    expect(within(list).queryByText("i18n:field_kind_formula")).toBeNull();
  });

  it("offers them when adding a column to an existing layer too", async () => {
    renderEditor({ layerId: "layer-1", geometryType: "polygon" });
    const list = await openKindSelector();
    expect(within(list).getByText("i18n:field_kind_serial")).toBeTruthy();
    expect(within(list).getByText("i18n:field_kind_uuid")).toBeTruthy();
    expect(within(list).getByText("i18n:field_kind_area")).toBeTruthy();
  });

  it("switching to serial offers a start number, and stores it", async () => {
    const onChange = renderEditor();
    const list = await openKindSelector();
    fireEvent.click(within(list).getByText("i18n:field_kind_serial"));
    expect(onChange).toHaveBeenLastCalledWith([expect.objectContaining({ kind: "serial" })]);
  });

  it("a serial field shows its start and the automatic-numbering hint", () => {
    const onChange = renderEditor({ fields: [field({ kind: "serial" })] });
    expect(screen.getByText("i18n:serial_field_hint")).toBeTruthy();
    const start = screen.getByTestId("serial-start") as HTMLInputElement;
    expect(start.value).toBe("");
    expect(start.placeholder).toBe("1");
    fireEvent.change(start, { target: { value: "1000" } });
    expect(onChange).toHaveBeenLastCalledWith([expect.objectContaining({ kind: "serial", start: 1000 })]);
  });

  it("refuses a start that is no whole number from 0", () => {
    const onChange = renderEditor({ fields: [field({ kind: "serial" })] });
    const start = screen.getByTestId("serial-start");
    fireEvent.change(start, { target: { value: "-3" } });
    fireEvent.change(start, { target: { value: "1.5" } });
    expect(onChange).not.toHaveBeenCalled();
  });

  it("an existing serial column's start is fixed", () => {
    renderEditor({ fields: [field({ kind: "serial", start: 100 })], lockedFieldIds: new Set(["f1"]) });
    const start = screen.getByTestId("serial-start") as HTMLInputElement;
    expect(start.value).toBe("100");
    expect(start.disabled).toBe(true);
    expect(screen.getByText("i18n:serial_start_fixed")).toBeTruthy();
  });

  it("a UUID field has no start, only its hint", () => {
    renderEditor({ fields: [field({ kind: "uuid" })] });
    expect(screen.getByText("i18n:uuid_field_hint")).toBeTruthy();
    expect(screen.queryByTestId("serial-start")).toBeNull();
  });

  it("leaving serial drops the start", async () => {
    const onChange = renderEditor({ fields: [field({ kind: "serial", start: 5 })] });
    const list = await openKindSelector();
    fireEvent.click(within(list).getByText("i18n:field_kind_number"));
    const [next] = onChange.mock.lastCall![0] as FieldDefinition[];
    expect(next.kind).toBe("number");
    expect(next.start).toBeUndefined();
  });
});

describe("FieldEditor converting an existing column", () => {
  it("offers only the allowed kinds on an existing field instead of disabling it", async () => {
    renderEditor({
      fields: [field({ kind: "number" })],
      lockedFieldIds: new Set(["f1"]),
      kindChoicesByField: { f1: ["number", "serial"] },
    });
    // The type selector is the first combobox; a number field also has its
    // format options.
    const user = userEvent.setup();
    await user.click(screen.getAllByRole("combobox")[0]);
    const list = await screen.findByRole("listbox");
    expect(within(list).getByText("i18n:field_kind_serial")).toBeTruthy();
    expect(within(list).getByText("i18n:field_kind_number")).toBeTruthy();
    expect(within(list).queryByText("i18n:field_kind_text")).toBeNull();
    expect(within(list).queryByText("i18n:field_kind_uuid")).toBeNull();
  });

  it("an existing column becoming a serial takes a start", () => {
    renderEditor({
      fields: [field({ kind: "serial" })],
      lockedFieldIds: new Set(["f1"]),
      kindChoicesByField: { f1: ["number", "serial"] },
      startEditableFieldIds: new Set(["f1"]),
    });
    const start = screen.getByTestId("serial-start") as HTMLInputElement;
    expect(start.disabled).toBe(false);
    expect(screen.getByText("i18n:serial_start_help")).toBeTruthy();
  });
});
