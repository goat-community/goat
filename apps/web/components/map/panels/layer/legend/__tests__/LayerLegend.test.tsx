import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LayerLegendPanel } from "@/components/map/panels/layer/legend/LayerLegend";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const categoryProperties = {
  color_field: { name: "category" },
  color_scale: "ordinal",
  color_range: {
    color_map: [
      [["clothes"], "#e74c3c"],
      [["other_grocery"], "#e67e22"],
      [["supermarket"], "#2ecc71"],
    ],
  },
};

const renderPanel = (props: Partial<React.ComponentProps<typeof LayerLegendPanel>> = {}) =>
  render(
    <LayerLegendPanel
      properties={categoryProperties}
      geometryType="point"
      compact
      {...props}
    />
  );

describe("LayerLegendPanel legend rows", () => {
  it("renders one row with an icon per category", () => {
    const { container } = renderPanel();

    expect(screen.getByText("clothes")).toBeTruthy();
    expect(screen.getByText("other_grocery")).toBeTruthy();
    expect(screen.getByText("supermarket")).toBeTruthy();
    expect(container.querySelectorAll("svg")).toHaveLength(3);
  });

  it("hides the whole row, icon included, when its label is cleared", () => {
    const { container } = renderPanel({
      editable: true,
      textOverrides: { item_0: "" },
    });

    expect(screen.queryByText("clothes")).toBeNull();
    expect(screen.getByText("other_grocery")).toBeTruthy();
    expect(screen.getByText("supermarket")).toBeTruthy();
    // The cleared row's icon must go with it, not linger as an orphan.
    expect(container.querySelectorAll("svg")).toHaveLength(2);
  });

  it("keeps later rows on their own override keys when an earlier row is hidden", () => {
    renderPanel({
      editable: true,
      textOverrides: { item_0: "", item_1: "Lebensmittel" },
    });

    // item_1 still addresses the second row even though the first is hidden.
    expect(screen.getByText("Lebensmittel")).toBeTruthy();
    expect(screen.getByText("supermarket")).toBeTruthy();
  });

  it("ignores overrides when the legend is not editable", () => {
    const { container } = renderPanel({ editable: false, textOverrides: { item_0: "" } });

    expect(screen.getByText("clothes")).toBeTruthy();
    expect(container.querySelectorAll("svg")).toHaveLength(3);
  });

  it("shows a label saved with the no-break spaces of inline editing as wrappable text", () => {
    renderPanel({ editable: true, textOverrides: { item_1: "Lebensmittel\u00a0und Getränke\u00a0" } });

    expect(screen.getByText("Lebensmittel und Getränke").textContent).toBe("Lebensmittel und Getränke");
  });

  it("saves an edited label without no-break spaces and only when it changed", () => {
    const onTextSave = vi.fn();
    renderPanel({ editable: true, textOverrides: { item_1: "Lebensmittel" }, onTextSave });

    const label = screen.getByText("Lebensmittel");
    label.textContent = "Lebensmittel\u00a0und Getränke\u00a0";
    fireEvent.blur(label);
    expect(onTextSave).toHaveBeenCalledWith("item_1", "Lebensmittel und Getränke");

    onTextSave.mockClear();
    const unchanged = screen.getByText("supermarket");
    unchanged.textContent = "supermarket\u00a0";
    fireEvent.blur(unchanged);
    expect(onTextSave).not.toHaveBeenCalled();
  });
});
