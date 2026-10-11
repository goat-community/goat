import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { WorkflowVariable } from "@/lib/validations/workflow";

import type { ProcessedInput } from "@/types/map/ogc-processes";

import VariableAwareInput, { filterVariables } from "@/components/workflows/inputs/VariableAwareInput";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (k: string) => k }) }));
// Only the variable-capable path is under test; the generic inputs pull in the
// whole toolbox.
vi.mock("@/components/map/panels/toolbox/generic/inputs", () => ({
  GenericInput: () => <div data-testid="generic-input" />,
}));

const labelled: WorkflowVariable = {
  id: "var-1",
  name: "max_abstand_gruppierung",
  label: "Maximaler Abstand",
  description: "Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern.",
  type: "number",
  defaultValue: 250,
  order: 0,
};
const legacy: WorkflowVariable = { id: "var-2", name: "radius", type: "number", order: 1 };
const text: WorkflowVariable = {
  id: "var-3",
  name: "suffix",
  label: "Namenszusatz",
  type: "string",
  order: 2,
};

const numberInput = {
  name: "distance",
  title: "Distance",
  inputType: "number",
  required: true,
  schema: { type: "number" },
  isLayerInput: false,
  metadata: [],
  fieldOrder: 0,
} as unknown as ProcessedInput;

const renderInput = (value: unknown = undefined, onChange = vi.fn()) => {
  render(
    <VariableAwareInput
      input={numberInput}
      value={value}
      onChange={onChange}
      variables={[labelled, legacy, text]}
    />
  );
  return onChange;
};

describe("VariableAwareInput", () => {
  it("lists compatible variables by label, with the technical name beside it", () => {
    renderInput();

    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_insert" }));
    const items = screen.getAllByRole("menuitem");
    // A number input offers number variables only.
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent("Maximaler Abstand");
    expect(items[0]).toHaveTextContent("{{@max_abstand_gruppierung}}");
    expect(items[1]).toHaveTextContent("radius");
  });

  it("inserts the technical reference when a labelled variable is picked", () => {
    const onChange = renderInput();

    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_insert" }));
    fireEvent.click(screen.getByText("Maximaler Abstand"));
    expect(onChange).toHaveBeenCalledWith("{{@max_abstand_gruppierung}}");
  });

  it("offers matching variables by label while a reference is typed", () => {
    renderInput();

    fireEvent.change(screen.getByRole("textbox"), { target: { value: "{{@abstand" } });
    const item = screen.getByRole("menuitem");
    expect(within(item).getByText("Maximaler Abstand")).toBeInTheDocument();
  });

  it("shows the referenced variable's label under the field, with its description on hover", async () => {
    renderInput("{{@max_abstand_gruppierung}}");

    const label = screen.getByTestId("variable-reference-label");
    expect(label).toHaveTextContent("Maximaler Abstand");
    fireEvent.mouseOver(label);
    expect(await screen.findByRole("tooltip")).toHaveTextContent(labelled.description!);
  });

  it("shows no label under a reference to an unlabelled variable", () => {
    renderInput("{{@radius}}");
    expect(screen.queryByTestId("variable-reference-label")).not.toBeInTheDocument();
  });

  it("still flags a reference to an unknown variable", () => {
    renderInput("{{@gone}}");
    expect(screen.getByText("workflow_variable_undefined")).toBeInTheDocument();
  });
});

describe("filterVariables", () => {
  const all = [labelled, legacy, text];

  it("returns everything for an empty filter", () => {
    expect(filterVariables(all, "")).toEqual(all);
  });

  it("matches names by prefix, as before", () => {
    expect(filterVariables(all, "max_").map((v) => v.name)).toEqual(["max_abstand_gruppierung"]);
    expect(filterVariables(all, "RAD").map((v) => v.name)).toEqual(["radius"]);
  });

  it("matches labels anywhere, ignoring case", () => {
    expect(filterVariables(all, "abstand").map((v) => v.name)).toEqual(["max_abstand_gruppierung"]);
    expect(filterVariables(all, "zusatz").map((v) => v.name)).toEqual(["suffix"]);
  });
});
