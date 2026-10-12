import { describe, expect, it } from "vitest";

import { edgeDerivedInputHandles, sqlInputsByHandle } from "@/lib/utils/workflowHandles";

const edge = (target: string, targetHandle: string | null, id = `${target}-${targetHandle}`) =>
  ({ id, source: "src", target, targetHandle }) as never;

describe("edgeDerivedInputHandles", () => {
  it("returns the named handles pointing at the node", () => {
    const edges = [edge("tool-a", "input_layer_id"), edge("tool-a", "overlay_layer_id")];

    expect(edgeDerivedInputHandles(edges, "tool-a")).toEqual([
      "input_layer_id",
      "overlay_layer_id",
    ]);
  });

  it("deduplicates a handle two edges point at", () => {
    // Real case: three tool nodes in a saved workflow each had two edges into
    // `input_layer_id`, which rendered two handles with the same React key.
    const edges = [
      edge("tool-a", "input_layer_id", "e1"),
      edge("tool-a", "overlay_layer_id", "e2"),
      edge("tool-a", "input_layer_id", "e3"),
    ];

    expect(edgeDerivedInputHandles(edges, "tool-a")).toEqual([
      "input_layer_id",
      "overlay_layer_id",
    ]);
  });

  it("ignores edges into other nodes", () => {
    const edges = [edge("tool-a", "input_layer_id"), edge("tool-b", "join_layer_id")];

    expect(edgeDerivedInputHandles(edges, "tool-a")).toEqual(["input_layer_id"]);
  });

  it("ignores the generic handle and edges with none", () => {
    const edges = [edge("tool-a", "input"), edge("tool-a", null)];

    expect(edgeDerivedInputHandles(edges, "tool-a")).toEqual([]);
  });
});

describe("sqlInputsByHandle", () => {
  const sqlEdge = (source: string, targetHandle: string | null) => ({ source, targetHandle });

  it("numbers the connected inputs from 1 in handle order, as the workflow runner compacts them", () => {
    // Drawn out of order and with handle 1 empty: the runner still registers input_1 and input_2.
    const inputs = sqlInputsByHandle([sqlEdge("b", "input_layer_3_id"), sqlEdge("a", "input_layer_2_id")]);

    expect(inputs.map((i) => [i.handle, i.alias, i.edge.source])).toEqual([
      ["input_layer_2_id", "input_1", "a"],
      ["input_layer_3_id", "input_2", "b"],
    ]);
  });

  it("lists a handle fed by two edges once, keeping the last edge as the runner does", () => {
    const inputs = sqlInputsByHandle([sqlEdge("if-true", "input_layer_1_id"), sqlEdge("if-false", "input_layer_1_id")]);

    expect(inputs).toHaveLength(1);
    expect(inputs[0].edge.source).toBe("if-false");
  });

  it("treats an edge without a handle as input 1", () => {
    expect(sqlInputsByHandle([sqlEdge("a", null)])[0]).toMatchObject({ handle: "input_layer_1_id", alias: "input_1" });
  });
});
