import { describe, expect, it } from "vitest";

import { cleanEditedText } from "@/lib/utils/editableText";

describe("cleanEditedText", () => {
  it("turns the no-break spaces a contentEditable writes into spaces the text can wrap at", () => {
    expect(cleanEditedText("Bus stops (as of 2026)")).toBe("Bus stops (as of 2026)");
  });

  it("drops the trailing space a label was left with", () => {
    expect(cleanEditedText("Bike parking ")).toBe("Bike parking");
    expect(cleanEditedText("  Legende ")).toBe("Legende");
  });

  it("leaves a cleared label empty", () => {
    expect(cleanEditedText(" ")).toBe("");
  });

  it("keeps other characters as they are", () => {
    expect(cleanEditedText("Grünflächen und Spielplätze")).toBe("Grünflächen und Spielplätze");
  });
});
