import { describe, expect, it } from "vitest";

import {
  WORKFLOW_VARIABLE_DESCRIPTION_MAX,
  WORKFLOW_VARIABLE_LABEL_MAX,
  getVariableDescription,
  getVariableDisplayName,
  hasVariableLabel,
  workflowConfigSchema,
  workflowVariableSchema,
} from "@/lib/validations/workflow";

const legacy = { id: "var-1", name: "max_abstand_gruppierung", type: "number", defaultValue: 250, order: 0 };

describe("workflowVariableSchema", () => {
  it("accepts a variable saved before labels existed, and adds neither key", () => {
    const parsed = workflowVariableSchema.parse(legacy);
    expect(parsed).toEqual(legacy);
    expect(parsed).not.toHaveProperty("label");
    expect(parsed).not.toHaveProperty("description");
  });

  it("accepts and keeps a label and a description", () => {
    const parsed = workflowVariableSchema.parse({
      ...legacy,
      label: "Maximaler Abstand",
      description: "Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern.",
    });
    expect(parsed.label).toBe("Maximaler Abstand");
    expect(parsed.description).toBe("Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern.");
  });

  it("caps the label at its limit", () => {
    expect(WORKFLOW_VARIABLE_LABEL_MAX).toBe(120);
    expect(
      workflowVariableSchema.safeParse({ ...legacy, label: "a".repeat(WORKFLOW_VARIABLE_LABEL_MAX) }).success
    ).toBe(true);
    expect(
      workflowVariableSchema.safeParse({ ...legacy, label: "a".repeat(WORKFLOW_VARIABLE_LABEL_MAX + 1) })
        .success
    ).toBe(false);
  });

  it("caps the description at its limit", () => {
    expect(WORKFLOW_VARIABLE_DESCRIPTION_MAX).toBe(500);
    expect(
      workflowVariableSchema.safeParse({
        ...legacy,
        description: "a".repeat(WORKFLOW_VARIABLE_DESCRIPTION_MAX),
      }).success
    ).toBe(true);
    expect(
      workflowVariableSchema.safeParse({
        ...legacy,
        description: "a".repeat(WORKFLOW_VARIABLE_DESCRIPTION_MAX + 1),
      }).success
    ).toBe(false);
  });

  it("allows any text in the label while the name stays an identifier", () => {
    expect(
      workflowVariableSchema.safeParse({ ...legacy, label: "Max. Abstand (m) – Gruppierung" }).success
    ).toBe(true);
    expect(
      workflowVariableSchema.safeParse({ ...legacy, name: "Max Abstand", label: "Max Abstand" }).success
    ).toBe(false);
  });

  it("rejects a label or description that is not text", () => {
    expect(workflowVariableSchema.safeParse({ ...legacy, label: 42 }).success).toBe(false);
    expect(workflowVariableSchema.safeParse({ ...legacy, description: null }).success).toBe(false);
  });
});

describe("workflowConfigSchema", () => {
  it("parses a legacy config with unlabelled variables unchanged", () => {
    const parsed = workflowConfigSchema.parse({ nodes: [], edges: [], variables: [legacy] });
    expect(parsed.variables).toEqual([legacy]);
  });

  it("parses a config mixing labelled and unlabelled variables", () => {
    const labelled = { ...legacy, id: "var-2", name: "radius", label: "Radius", order: 1 };
    const parsed = workflowConfigSchema.parse({ nodes: [], edges: [], variables: [legacy, labelled] });
    expect(parsed.variables.map((v) => v.label)).toEqual([undefined, "Radius"]);
  });
});

describe("variable display helpers", () => {
  it("shows the label, falling back to the name", () => {
    expect(getVariableDisplayName({ name: "radius", label: "Suchradius" })).toBe("Suchradius");
    expect(getVariableDisplayName({ name: "radius" })).toBe("radius");
    expect(getVariableDisplayName({ name: "radius", label: "" })).toBe("radius");
    expect(getVariableDisplayName({ name: "radius", label: "   " })).toBe("radius");
    expect(getVariableDisplayName({ name: "radius", label: "  Suchradius " })).toBe("Suchradius");
  });

  it("knows when a label differs from the name", () => {
    expect(hasVariableLabel({ name: "radius", label: "Suchradius" })).toBe(true);
    expect(hasVariableLabel({ name: "radius" })).toBe(false);
    expect(hasVariableLabel({ name: "radius", label: "radius" })).toBe(false);
  });

  it("returns a description only when there is text", () => {
    expect(getVariableDescription({ description: "In Metern" })).toBe("In Metern");
    expect(getVariableDescription({ description: "  " })).toBeUndefined();
    expect(getVariableDescription({})).toBeUndefined();
  });
});
