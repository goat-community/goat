/**
 * A serial number or UUID in the attribute panel: read-only, "assigned
 * automatically" while a new feature has none yet, the value once it has.
 */
import { configureStore } from "@reduxjs/toolkit";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { describe, expect, it, vi } from "vitest";

import { featureEditorReducer } from "@/lib/store/featureEditor/slice";

import FeatureEditPanel from "@/components/map/panels/FeatureEditPanel";

vi.mock("@/lib/providers/DrawProvider", () => ({ useDraw: () => ({ drawControl: null }) }));
vi.mock("@/hooks/map/CommonHooks", () => ({
  default: () => ({
    layerFields: [
      { name: "vorhaben_id", type: "number", kind: "serial", is_generated: true, display_config: {} },
      { name: "uid", type: "string", kind: "uuid", is_generated: true, display_config: {} },
      { name: "titel", type: "string", kind: "string", display_config: {} },
    ],
    isLoading: false,
    isError: false,
  }),
}));
vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (k: string) => `i18n:${k}` }) }));

const UID = "0625b5a7-50e1-4cfa-8392-7b0852e0d980";

const storeWith = (mode: "draw" | "select", properties: Record<string, unknown>) =>
  configureStore({
    reducer: { featureEditor: featureEditorReducer },
    preloadedState: {
      featureEditor: {
        activeLayerId: "layer-1",
        geometryType: "point",
        mode,
        activeFeatureId: "feat-1",
        isSaving: false,
        undoStack: [],
        redoStack: [],
        pendingFeatures: {
          "feat-1": {
            id: "feat-1",
            drawFeatureId: null,
            geometry: { type: "Point" as const, coordinates: [0, 0] },
            properties,
            committed: mode !== "draw",
            action: mode === "draw" ? ("create" as const) : ("update" as const),
            originalGeometry: { type: "Point" as const, coordinates: [0, 0] },
            originalProperties: properties,
          },
        },
      },
    },
  });

// The panel lists the layer's fields in order, each label above its input.
const FIELD_ORDER = ["vorhaben_id", "uid", "titel"];
const inputOf = (name: string) => {
  expect(screen.getByText(name)).toBeTruthy();
  return screen.getAllByRole("textbox")[FIELD_ORDER.indexOf(name)] as HTMLInputElement;
};

describe("FeatureEditPanel generated fields", () => {
  it("while drawing: read-only, assigned automatically", () => {
    render(
      <Provider store={storeWith("draw", {})}>
        <FeatureEditPanel />
      </Provider>
    );
    for (const name of ["vorhaben_id", "uid"]) {
      const input = inputOf(name);
      expect(input.disabled, name).toBe(true);
      expect(input.value, name).toBe("");
      expect(input.placeholder, name).toBe("i18n:assigned_automatically");
    }
    // An ordinary field stays editable.
    expect(inputOf("titel").disabled).toBe(false);
  });

  it("after saving: shows the assigned values, still read-only", () => {
    render(
      <Provider store={storeWith("select", { vorhaben_id: 42, uid: UID, titel: "A" })}>
        <FeatureEditPanel />
      </Provider>
    );
    expect(inputOf("vorhaben_id").value).toBe("42");
    expect(inputOf("vorhaben_id").disabled).toBe(true);
    expect(inputOf("uid").value).toBe(UID);
    expect(inputOf("uid").disabled).toBe(true);
  });
});
