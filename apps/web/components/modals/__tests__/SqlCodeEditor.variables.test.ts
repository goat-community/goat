import { EditorState } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { describe, expect, it } from "vitest";

import { variableCompletionOption } from "@/components/modals/SqlCodeEditor";

describe("SQL editor variable completions", () => {
  it("shows a labelled variable by its label, with the name to type in the detail", () => {
    const option = variableCompletionOption(
      {
        name: "max_abstand_gruppierung",
        type: "number",
        label: "Maximaler Abstand",
        description: "In Metern.",
      },
      0
    );

    // Matching still runs on the name: that is what is typed after {{@.
    expect(option.label).toBe("max_abstand_gruppierung");
    expect(option.displayLabel).toBe("Maximaler Abstand");
    expect(option.detail).toBe("max_abstand_gruppierung · number");
    expect(option.info).toBe("In Metern.");
  });

  it("keeps an unlabelled variable's option as it was", () => {
    const option = variableCompletionOption({ name: "radius", type: "number" }, 0);

    expect(option.label).toBe("radius");
    expect(option).not.toHaveProperty("displayLabel");
    expect(option.detail).toBe("number");
    expect(option).not.toHaveProperty("info");
  });

  it("treats a blank label or description as none", () => {
    const option = variableCompletionOption(
      { name: "radius", type: "number", label: " ", description: "" },
      0
    );

    expect(option).not.toHaveProperty("displayLabel");
    expect(option.detail).toBe("number");
    expect(option).not.toHaveProperty("info");
  });

  it("inserts the technical reference, not the label", () => {
    const doc = "SELECT {{@max";
    const view = new EditorView({ state: EditorState.create({ doc }) });
    const option = variableCompletionOption(
      { name: "max_abstand_gruppierung", type: "number", label: "Maximaler Abstand" },
      0
    );
    const apply = option.apply as (view: EditorView, c: typeof option, from: number, to: number) => void;
    apply(view, option, doc.length - "max".length, doc.length);

    expect(view.state.doc.toString()).toBe("SELECT {{@max_abstand_gruppierung}}");
    view.destroy();
  });
});
