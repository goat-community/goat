import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { WorkflowVariable } from "@/lib/validations/workflow";

import WorkflowRunVariableField from "@/components/map/panels/toolbox/WorkflowRunVariableField";

const labelled: WorkflowVariable = {
  id: "var-1",
  name: "max_abstand_gruppierung",
  label: "Maximaler Abstand",
  description: "Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern.",
  type: "number",
  defaultValue: 250,
  order: 0,
};
const legacy: WorkflowVariable = { id: "var-2", name: "suffix", type: "string", order: 1 };

describe("WorkflowRunVariableField", () => {
  it("titles the field with the label and gives the description as help text", () => {
    render(<WorkflowRunVariableField variable={labelled} value={250} onChange={vi.fn()} />);

    expect(screen.getByText("Maximaler Abstand")).toBeInTheDocument();
    expect(screen.getByText(labelled.description!)).toBeInTheDocument();
    const field = screen.getByRole("spinbutton", { name: "Maximaler Abstand" }) as HTMLInputElement;
    expect(field.value).toBe("250");
    expect(screen.queryByText("max_abstand_gruppierung")).not.toBeInTheDocument();
  });

  it("falls back to the name for a variable without a label", () => {
    render(<WorkflowRunVariableField variable={legacy} value="" onChange={vi.fn()} />);

    expect(screen.getByRole("textbox", { name: "suffix" })).toBeInTheDocument();
  });

  it("reports numbers as numbers and text as text", () => {
    const onNumber = vi.fn();
    const { unmount } = render(
      <WorkflowRunVariableField variable={labelled} value={250} onChange={onNumber} />
    );
    fireEvent.change(screen.getByRole("spinbutton"), { target: { value: "300" } });
    expect(onNumber).toHaveBeenCalledWith(300);
    unmount();

    const onText = vi.fn();
    render(<WorkflowRunVariableField variable={legacy} value="" onChange={onText} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "_neu" } });
    expect(onText).toHaveBeenCalledWith("_neu");
  });
});
