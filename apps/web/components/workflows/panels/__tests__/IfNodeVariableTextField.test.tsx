import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { WorkflowVariable } from "@/lib/validations/workflow";

import { VariableTextField } from "@/components/workflows/panels/IfNodeSettings";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (k: string) => k }) }));

const labelled: WorkflowVariable = {
  id: "var-1",
  name: "schwellenwert",
  label: "Schwellenwert Einwohner",
  description: "Ab dieser Einwohnerzahl gilt die Bedingung.",
  type: "number",
  order: 0,
};
const legacy: WorkflowVariable = { id: "var-2", name: "radius", type: "number", order: 1 };

describe("if node VariableTextField", () => {
  it("lists variables by label with the technical reference beside it", () => {
    render(<VariableTextField value="" onChange={vi.fn()} variables={[labelled, legacy]} />);

    fireEvent.click(screen.getByRole("button", { name: "insert_variable" }));
    const items = screen.getAllByRole("menuitem");
    expect(items[0]).toHaveTextContent("Schwellenwert Einwohner");
    expect(items[0]).toHaveTextContent("{{@schwellenwert}}");
    expect(items[1]).toHaveTextContent("radius");
  });

  it("inserts the technical reference when a labelled variable is picked", () => {
    const onChange = vi.fn();
    render(<VariableTextField value="" onChange={onChange} variables={[labelled, legacy]} />);

    fireEvent.click(screen.getByRole("button", { name: "insert_variable" }));
    fireEvent.click(screen.getByText("Schwellenwert Einwohner"));
    expect(onChange).toHaveBeenCalledWith("{{@schwellenwert}}");
  });

  it("shows the description of a variable in the menu on hover", async () => {
    render(<VariableTextField value="" onChange={vi.fn()} variables={[labelled]} />);

    fireEvent.click(screen.getByRole("button", { name: "insert_variable" }));
    fireEvent.mouseOver(screen.getByRole("menuitem"));
    expect(await screen.findByRole("tooltip")).toHaveTextContent(labelled.description!);
  });

  it("shows the label of the variable the field refers to", () => {
    render(<VariableTextField value="{{@schwellenwert}}" onChange={vi.fn()} variables={[labelled]} />);
    expect(screen.getByText("Schwellenwert Einwohner")).toBeInTheDocument();
  });

  it("shows nothing extra for an unlabelled variable or free text", () => {
    const { container, rerender } = render(
      <VariableTextField value="{{@radius}}" onChange={vi.fn()} variables={[legacy]} />
    );
    expect(container.querySelector(".MuiFormHelperText-root")).toBeNull();

    rerender(<VariableTextField value="Text {{@schwellenwert}}" onChange={vi.fn()} variables={[labelled]} />);
    expect(container.querySelector(".MuiFormHelperText-root")).toBeNull();
  });
});
