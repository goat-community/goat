import { describe, expect, it } from "vitest";

import { LABEL_FONT } from "@/lib/constants/basemaps";

import { getSymbolStyleSpec } from "../layer";

describe("getSymbolStyleSpec", () => {
  it("draws text labels in the label font", () => {
    const layer = { id: "abc-123", properties: {} } as unknown as Parameters<typeof getSymbolStyleSpec>[1];
    const spec = getSymbolStyleSpec({ field: "name" } as Parameters<typeof getSymbolStyleSpec>[0], layer);
    expect((spec.layout as Record<string, unknown>)["text-font"]).toEqual([LABEL_FONT]);
  });
});
