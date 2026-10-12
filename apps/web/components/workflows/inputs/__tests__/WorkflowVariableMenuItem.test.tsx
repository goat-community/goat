import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { WorkflowVariable } from "@/lib/validations/workflow";

import WorkflowVariableMenuItem from "@/components/workflows/inputs/WorkflowVariableMenuItem";

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

describe("WorkflowVariableMenuItem", () => {
  it("shows the label with the technical reference beside it", () => {
    render(<WorkflowVariableMenuItem variable={labelled} onSelect={vi.fn()} />);

    const item = screen.getByRole("menuitem");
    expect(item).toHaveTextContent("Maximaler Abstand");
    expect(item).toHaveTextContent("{{@max_abstand_gruppierung}}");
    expect(item).toHaveTextContent("number");
  });

  it("falls back to the name, shown once, for a variable without a label", () => {
    render(<WorkflowVariableMenuItem variable={legacy} onSelect={vi.fn()} />);

    const item = screen.getByRole("menuitem");
    expect(screen.getByText("radius")).toBeInTheDocument();
    expect(item).not.toHaveTextContent("{{@radius}}");
  });

  it("falls back to the name when the label is blank", () => {
    render(<WorkflowVariableMenuItem variable={{ ...legacy, label: "  " }} onSelect={vi.fn()} />);
    expect(screen.getByText("radius")).toBeInTheDocument();
  });

  it("shows the description as a tooltip on hover", async () => {
    render(<WorkflowVariableMenuItem variable={labelled} onSelect={vi.fn()} />);

    fireEvent.mouseOver(screen.getByRole("menuitem"));
    expect(await screen.findByRole("tooltip")).toHaveTextContent(
      "Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern."
    );
    // The tooltip describes the item; it does not rename it.
    expect(screen.getByRole("menuitem")).not.toHaveAccessibleName(labelled.description!);
  });

  it("shows no tooltip without a description", async () => {
    render(<WorkflowVariableMenuItem variable={legacy} onSelect={vi.fn()} />);

    fireEvent.mouseOver(screen.getByRole("menuitem"));
    await new Promise((resolve) => setTimeout(resolve, 200));
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("hands the variable to onSelect when clicked", () => {
    const onSelect = vi.fn();
    render(<WorkflowVariableMenuItem variable={labelled} onSelect={onSelect} />);

    fireEvent.click(screen.getByRole("menuitem"));
    expect(onSelect).toHaveBeenCalledWith(labelled);
  });
});
