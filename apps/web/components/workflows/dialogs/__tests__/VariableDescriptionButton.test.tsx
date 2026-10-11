import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import VariableDescriptionButton from "@/components/workflows/dialogs/VariableDescriptionButton";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (k: string) => k }) }));

const TEXT = "Anteil der Nachfrage, den ein Standort abschöpft.";

const open = (name: string) => {
  fireEvent.click(screen.getByRole("button", { name }));
  return screen.getByRole("textbox", { name: "workflow_variable_description" }) as HTMLTextAreaElement;
};

/** The popover's invisible backdrop: clicking it closes the popover. */
const clickAway = () => {
  const backdrop = document.querySelector(".MuiPopover-root .MuiBackdrop-root");
  expect(backdrop).not.toBeNull();
  fireEvent.click(backdrop!);
};

describe("VariableDescriptionButton", () => {
  it("offers to add a description when there is none, with a muted outline icon", () => {
    render(<VariableDescriptionButton value={undefined} onChange={vi.fn()} />);

    const button = screen.getByRole("button", { name: "workflow_variable_description_add" });
    expect(button.getAttribute("data-has-description")).toBe("false");
    expect(screen.getByTestId("ChatBubbleOutlineIcon")).toBeInTheDocument();
    expect(screen.queryByTestId("ChatBubbleIcon")).not.toBeInTheDocument();
  });

  it("treats a blank description as none", () => {
    render(<VariableDescriptionButton value="   " onChange={vi.fn()} />);
    expect(screen.getByRole("button", { name: "workflow_variable_description_add" })).toBeInTheDocument();
  });

  it("shows a filled icon and the description as tooltip when there is one", async () => {
    render(<VariableDescriptionButton value={TEXT} onChange={vi.fn()} />);

    const button = screen.getByRole("button", { name: "workflow_variable_description_edit" });
    expect(button.getAttribute("data-has-description")).toBe("true");
    expect(screen.getByTestId("ChatBubbleIcon")).toBeInTheDocument();

    fireEvent.mouseOver(button);
    expect(await screen.findByRole("tooltip")).toHaveTextContent(TEXT);
  });

  it("names the action in the tooltip when there is no description", async () => {
    render(<VariableDescriptionButton value="" onChange={vi.fn()} />);

    fireEvent.mouseOver(screen.getByRole("button", { name: "workflow_variable_description_add" }));
    expect(await screen.findByRole("tooltip")).toHaveTextContent("workflow_variable_description_add");
  });

  it("opens a popover with the current text, a counter and the length limit", () => {
    render(<VariableDescriptionButton value={TEXT} onChange={vi.fn()} />);

    const field = open("workflow_variable_description_edit");
    expect(field.value).toBe(TEXT);
    expect(field.maxLength).toBe(500);
    expect(screen.getByText(`${TEXT.length} / 500`)).toBeInTheDocument();

    fireEvent.change(field, { target: { value: "Neu" } });
    expect(screen.getByText("3 / 500")).toBeInTheDocument();
  });

  it("saves the edit when the popover closes", async () => {
    const onChange = vi.fn();
    render(<VariableDescriptionButton value={undefined} onChange={onChange} />);

    fireEvent.change(open("workflow_variable_description_add"), { target: { value: TEXT } });
    clickAway();

    expect(onChange).toHaveBeenCalledWith(TEXT);
    await waitFor(() =>
      expect(screen.queryByRole("textbox", { name: "workflow_variable_description" })).not.toBeInTheDocument()
    );
  });

  it("saves the edit when the field loses focus, and keeps the popover open", () => {
    const onChange = vi.fn();
    render(<VariableDescriptionButton value={undefined} onChange={onChange} />);

    const field = open("workflow_variable_description_add");
    fireEvent.change(field, { target: { value: TEXT } });
    fireEvent.blur(field);

    expect(onChange).toHaveBeenCalledWith(TEXT);
    expect(screen.getByRole("textbox", { name: "workflow_variable_description" })).toBeInTheDocument();
  });

  it("discards the edit on Escape", async () => {
    const onChange = vi.fn();
    render(<VariableDescriptionButton value="Alt" onChange={onChange} />);

    const field = open("workflow_variable_description_edit");
    fireEvent.change(field, { target: { value: "Verworfen" } });
    fireEvent.keyDown(field, { key: "Escape" });
    fireEvent.blur(field);

    expect(onChange).not.toHaveBeenCalled();
    await waitFor(() =>
      expect(screen.queryByRole("textbox", { name: "workflow_variable_description" })).not.toBeInTheDocument()
    );
  });

  it("on Escape, also undoes what a blur already saved", () => {
    const onChange = vi.fn();
    const { rerender } = render(<VariableDescriptionButton value="Alt" onChange={onChange} />);

    const field = open("workflow_variable_description_edit");
    fireEvent.change(field, { target: { value: "Zwischenstand" } });
    fireEvent.blur(field);
    expect(onChange).toHaveBeenLastCalledWith("Zwischenstand");
    // The parent stores what the blur saved.
    rerender(<VariableDescriptionButton value="Zwischenstand" onChange={onChange} />);

    fireEvent.keyDown(screen.getByRole("textbox", { name: "workflow_variable_description" }), {
      key: "Escape",
    });
    expect(onChange).toHaveBeenLastCalledWith("Alt");
  });

  it("does not report a change when nothing was edited", () => {
    const onChange = vi.fn();
    render(<VariableDescriptionButton value={TEXT} onChange={onChange} />);

    const field = open("workflow_variable_description_edit");
    fireEvent.blur(field);
    clickAway();

    expect(onChange).not.toHaveBeenCalled();
  });

  it("flags a stored description that is too long", async () => {
    render(<VariableDescriptionButton value={"b".repeat(501)} onChange={vi.fn()} error="too long" />);

    const button = screen.getByRole("button", { name: "workflow_variable_description_edit" });
    expect(button.getAttribute("aria-invalid")).toBe("true");
    fireEvent.mouseOver(button);
    expect(await screen.findByRole("tooltip")).toHaveTextContent("too long");

    open("workflow_variable_description_edit");
    expect(screen.getByText("too long")).toBeInTheDocument();
  });
});
