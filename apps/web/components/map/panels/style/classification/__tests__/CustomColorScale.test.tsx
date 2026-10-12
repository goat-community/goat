import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ColorScaleSelectorProps } from "@/types/map/color";

import CustomColorScale from "../CustomColorScale";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (k: string) => k }),
}));

const colorRange = {
  name: "Custom",
  type: "custom",
  category: "Custom",
  colors: ["#FF0000", "#00FF00"],
  color_map: [
    [["a"], "#FF0000"],
    [["b"], "#00FF00"],
  ],
};

// Every style change in the panel deep-clones the layer style, so the parent
// hands back an equal color_map in a new array.
const props = (range: typeof colorRange, noDataColor?: string) =>
  ({
    selectedColorScaleMethod: "ordinal",
    setSelectedColorScaleMethod: vi.fn(),
    colorSet: { selectedColor: JSON.parse(JSON.stringify(range)), setColor: vi.fn(), isRange: true },
    activeLayerId: "layer-1",
    activeLayerField: { name: "kind", type: "string" },
    intervals: 2,
    noDataColor,
    onNoDataColorChange: vi.fn(),
    setIsClickAwayEnabled: vi.fn(),
  }) as unknown as ColorScaleSelectorProps & { setIsClickAwayEnabled: (v: boolean) => void };

const labelInputs = () => screen.getAllByPlaceholderText("legend_label") as HTMLInputElement[];

describe("CustomColorScale", () => {
  it("keeps unsaved row edits when an unrelated style change re-renders it", () => {
    const { rerender } = render(<CustomColorScale {...props(colorRange)} />);
    fireEvent.change(labelInputs()[0], { target: { value: "Edited" } });

    rerender(<CustomColorScale {...props(colorRange, "#CCCCCC")} />);

    expect(labelInputs()[0].value).toBe("Edited");
  });

  it("reloads the rows when the saved color map itself changes", () => {
    const { rerender } = render(<CustomColorScale {...props(colorRange)} />);
    fireEvent.change(labelInputs()[0], { target: { value: "Edited" } });

    const changed = {
      ...colorRange,
      color_map: [...colorRange.color_map, [["c"], "#0000FF"]],
    };
    rerender(<CustomColorScale {...props(changed)} />);

    expect(labelInputs()).toHaveLength(3);
    expect(labelInputs()[0].value).toBe("");
  });
});
