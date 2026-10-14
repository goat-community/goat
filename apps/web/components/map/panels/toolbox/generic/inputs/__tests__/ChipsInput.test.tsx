import { act, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";

import type { ProcessedInput } from "@/types/map/ogc-processes";

import ChipsInput from "@/components/map/panels/toolbox/generic/inputs/ChipsInput";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const INPUT = {
  name: "step_sizes",
  title: "Step sizes",
  uiMeta: {
    widget_options: { compute_from: { steps_field: "steps", limit_fields: [{ field: "max_cost" }] } },
  },
} as unknown as ProcessedInput;

let resetForm: () => void = () => undefined;

// The step sizes as GenericTool holds them: a reset to defaults empties them
// while steps and limit keep the values they had.
function Form({ limit = 15 }: { limit?: number }) {
  const [value, setValue] = useState<number[] | undefined>(undefined);
  resetForm = () => setValue(undefined);
  return (
    <ChipsInput input={INPUT} value={value} onChange={setValue} formValues={{ steps: 5, max_cost: limit }} />
  );
}

const chips = () => Array.from(document.querySelectorAll(".MuiChip-label")).map((el) => el.textContent);

describe("ChipsInput", () => {
  it("computes the step sizes from steps and limit", () => {
    render(<Form />);
    expect(chips()).toEqual(["3", "6", "9", "12", "15"]);
  });

  it("recomputes them when the limit changes", () => {
    const { rerender } = render(<Form />);
    rerender(<Form limit={30} />);
    expect(chips()).toEqual(["6", "12", "18", "24", "30"]);
  });

  it("recomputes them when the form is reset with steps and limit unchanged", () => {
    render(<Form />);
    act(() => resetForm());
    expect(chips()).toEqual(["3", "6", "9", "12", "15"]);
  });

  it("keeps them empty when the user deletes every chip", () => {
    render(<Form />);
    for (let i = 0; i < 5; i++) {
      fireEvent.click(screen.getAllByTestId("CancelIcon")[0]);
    }
    expect(chips()).toEqual([]);
  });
});
