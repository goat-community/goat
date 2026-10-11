import { fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { WorkflowVariable } from "@/lib/validations/workflow";

import WorkflowVariablesDialog, {
  normalizeVariable,
} from "@/components/workflows/dialogs/WorkflowVariablesDialog";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (k: string) => k }) }));

const dispatch = vi.fn();
// One array per test, not a fresh one per call: the dialog re-seeds its local
// copy whenever the selected variables change identity, so a new array each
// render would loop forever.
let storedVariables: WorkflowVariable[] = [];
vi.mock("react-redux", () => ({
  useDispatch: () => dispatch,
  useSelector: () => storedVariables,
}));

/** The variables the dialog's last save handed to the store. */
const savedVariables = (): WorkflowVariable[] => {
  const action = dispatch.mock.calls.at(-1)?.[0] as { type: string; payload: WorkflowVariable[] };
  expect(action.type).toBe("workflow/setVariables");
  return action.payload;
};

const done = () => fireEvent.click(screen.getByRole("button", { name: "done" }));

/** Close the description popover the way a click beside it does. */
const closePopover = () => {
  const backdrop = document.querySelector(".MuiPopover-root .MuiBackdrop-root");
  expect(backdrop).not.toBeNull();
  fireEvent.click(backdrop!);
};

const legacy: WorkflowVariable = {
  id: "var-1",
  name: "max_abstand_gruppierung",
  type: "number",
  defaultValue: 250,
  order: 0,
};

describe("WorkflowVariablesDialog", () => {
  beforeEach(() => {
    dispatch.mockReset();
    storedVariables = [];
  });

  it("renders the title, the empty state and the Done action", () => {
    render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

    expect(screen.getByText("workflow_variables")).toBeInTheDocument();
    expect(screen.getByText("workflow_variable_none_defined")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "done" })).toBeInTheDocument();
  });

  it("keeps the dialog open when a new variable has no name yet", () => {
    const onClose = vi.fn();
    render(<WorkflowVariablesDialog open onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_add" }));
    done();
    expect(onClose).not.toHaveBeenCalled();
    expect(screen.getByText("workflow_variable_name_required")).toBeInTheDocument();
  });

  describe("layout", () => {
    it("heads the columns Name, Label, Type, Default", () => {
      storedVariables = [legacy];
      render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

      expect(screen.getByTestId("workflow-variable-header").textContent).toBe(
        [
          "workflow_variable_name",
          "workflow_variable_label",
          "workflow_variable_type",
          "workflow_variable_default",
        ].join("")
      );
    });

    it("puts each variable on one row: name, label, type, default, description, delete", () => {
      storedVariables = [
        legacy,
        { id: "var-2", name: "agglomerationseffekt_entfernung", type: "number", defaultValue: 200, order: 1 },
      ];
      render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

      const rows = screen.getAllByTestId("workflow-variable-row");
      expect(rows).toHaveLength(2);
      for (const row of rows) {
        const r = within(row);
        const name = r.getByRole("textbox", { name: "workflow_variable_name" });
        const label = r.getByRole("textbox", { name: "workflow_variable_label" });
        const defaultValue = r.getByRole("spinbutton", { name: "workflow_variable_default" });
        const description = r.getByRole("button", { name: "workflow_variable_description_add" });
        const remove = r.getByRole("button", { name: "delete" });
        // In this order, left to right.
        const order = [name, label, defaultValue, description, remove];
        for (let i = 1; i < order.length; i++) {
          expect(
            order[i - 1].compareDocumentPosition(order[i]) & Node.DOCUMENT_POSITION_FOLLOWING
          ).toBeTruthy();
        }
        // No second line: the description is not edited in the row.
        expect(r.queryByRole("textbox", { name: "workflow_variable_description" })).toBeNull();
      }
    });

    it("uses the short placeholder for the label and keeps full values in a title", () => {
      storedVariables = [{ ...legacy, label: "Maximaler Abstand der Gruppierung" }];
      render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

      const name = screen.getByRole("textbox", { name: "workflow_variable_name" });
      const label = screen.getByRole("textbox", { name: "workflow_variable_label" }) as HTMLInputElement;
      expect(label.placeholder).toBe("workflow_variable_label_placeholder");
      expect(name.getAttribute("title")).toBe("max_abstand_gruppierung");
      expect(label.getAttribute("title")).toBe("Maximaler Abstand der Gruppierung");
    });

    it("limits what can be typed into the label to the schema's length", () => {
      storedVariables = [legacy];
      render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

      // Read off the DOM property rather than a matcher: the repo's ESLint setup
      // reads jest-dom's attribute matchers as Playwright's (async) ones.
      const label = screen.getByRole("textbox", { name: "workflow_variable_label" }) as HTMLInputElement;
      expect(label.maxLength).toBe(120);
    });
  });

  it("saves a new variable with the label typed in and a description from the popover, trimmed", () => {
    const onClose = vi.fn();
    render(<WorkflowVariablesDialog open onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_add" }));
    fireEvent.change(screen.getByRole("textbox", { name: "workflow_variable_name" }), {
      target: { value: "max_abstand_gruppierung" },
    });
    fireEvent.change(screen.getByRole("textbox", { name: "workflow_variable_label" }), {
      target: { value: "  Maximaler Abstand  " },
    });
    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_description_add" }));
    const description = screen.getByRole("textbox", { name: "workflow_variable_description" });
    fireEvent.change(description, { target: { value: " Größter Abstand in einer Gruppe. " } });
    closePopover();
    done();

    expect(onClose).toHaveBeenCalled();
    expect(savedVariables()).toEqual([
      expect.objectContaining({
        name: "max_abstand_gruppierung",
        label: "Maximaler Abstand",
        description: "Größter Abstand in einer Gruppe.",
      }),
    ]);
  });

  it("marks a variable with a description and lets it be edited", () => {
    storedVariables = [{ ...legacy, label: "Abstand", description: "Alt" }];
    render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

    const label = screen.getByRole("textbox", { name: "workflow_variable_label" }) as HTMLInputElement;
    expect(label.value).toBe("Abstand");
    const button = screen.getByRole("button", { name: "workflow_variable_description_edit" });
    expect(button.getAttribute("data-has-description")).toBe("true");

    fireEvent.change(label, { target: { value: "Maximaler Abstand" } });
    fireEvent.click(button);
    const description = screen.getByRole("textbox", {
      name: "workflow_variable_description",
    }) as HTMLTextAreaElement;
    expect(description.value).toBe("Alt");
    fireEvent.change(description, { target: { value: "Neu" } });
    fireEvent.blur(description);
    closePopover();
    done();

    expect(savedVariables()).toEqual([
      { ...legacy, label: "Maximaler Abstand", description: "Neu", order: 0 },
    ]);
  });

  it("keeps the stored description when its edit is cancelled with Escape", () => {
    storedVariables = [{ ...legacy, description: "Alt" }];
    render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_description_edit" }));
    const description = screen.getByRole("textbox", { name: "workflow_variable_description" });
    fireEvent.change(description, { target: { value: "Verworfen" } });
    fireEvent.keyDown(description, { key: "Escape" });
    done();

    expect(savedVariables()[0].description).toBe("Alt");
  });

  it("saves a legacy variable without adding label or description keys", () => {
    storedVariables = [legacy];
    render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

    done();

    const [saved] = savedVariables();
    expect(saved).toEqual(legacy);
    expect(saved).not.toHaveProperty("label");
    expect(saved).not.toHaveProperty("description");
  });

  it("drops a label or description cleared to whitespace", () => {
    storedVariables = [{ ...legacy, label: "Abstand", description: "Alt" }];
    render(<WorkflowVariablesDialog open onClose={vi.fn()} />);

    fireEvent.change(screen.getByRole("textbox", { name: "workflow_variable_label" }), {
      target: { value: "   " },
    });
    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_description_edit" }));
    const description = screen.getByRole("textbox", { name: "workflow_variable_description" });
    fireEvent.change(description, { target: { value: "  " } });
    closePopover();
    done();

    const [saved] = savedVariables();
    expect(saved).not.toHaveProperty("label");
    expect(saved).not.toHaveProperty("description");
  });

  it("refuses to save an over-long label or description that came from stored data", () => {
    storedVariables = [{ ...legacy, label: "a".repeat(121), description: "b".repeat(501) }];
    const onClose = vi.fn();
    render(<WorkflowVariablesDialog open onClose={onClose} />);

    done();

    expect(onClose).not.toHaveBeenCalled();
    expect(dispatch).not.toHaveBeenCalled();
    expect(screen.getByText("workflow_variable_label_too_long")).toBeInTheDocument();
    const button = screen.getByRole("button", { name: "workflow_variable_description_edit" });
    expect(button.getAttribute("aria-invalid")).toBe("true");
  });

  it("does not let a label stand in for a missing name", () => {
    const onClose = vi.fn();
    render(<WorkflowVariablesDialog open onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "workflow_variable_add" }));
    fireEvent.change(screen.getByRole("textbox", { name: "workflow_variable_label" }), {
      target: { value: "Maximaler Abstand" },
    });
    done();

    expect(onClose).not.toHaveBeenCalled();
    expect(screen.getByText("workflow_variable_name_required")).toBeInTheDocument();
  });
});

describe("normalizeVariable", () => {
  it("recomputes the order and coerces a number default as before", () => {
    expect(normalizeVariable({ ...legacy, defaultValue: "12", order: 7 }, 2)).toEqual({
      ...legacy,
      defaultValue: 12,
      order: 2,
    });
  });

  it("trims label and description and leaves out empty ones", () => {
    expect(normalizeVariable({ ...legacy, label: " A ", description: " B " }, 0)).toEqual({
      ...legacy,
      label: "A",
      description: "B",
    });
    const cleared = normalizeVariable({ ...legacy, label: "", description: "  " }, 0);
    expect(cleared).not.toHaveProperty("label");
    expect(cleared).not.toHaveProperty("description");
  });

  it("keeps only the schema's keys", () => {
    const stray = { ...legacy, comment: "from an old draft" } as WorkflowVariable;
    expect(normalizeVariable(stray, 0)).not.toHaveProperty("comment");
  });

  it("adds no default to a variable that never had one", () => {
    const { defaultValue: _unused, ...withoutDefault } = legacy;
    void _unused;
    expect(normalizeVariable(withoutDefault, 0)).not.toHaveProperty("defaultValue");
  });
});
