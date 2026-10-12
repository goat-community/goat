import type { Edge } from "@xyflow/react";

/** The generic input handle a node without named inputs exposes. */
const DEFAULT_INPUT_HANDLE = "input";

/**
 * The named input handles a node must render, read off its incoming edges.
 *
 * Used until the process description loads and the real input list is known.
 * Two edges may target the same handle — a user can wire two sources into one
 * input — so the names are deduplicated: they become React keys and handle ids,
 * and a repeated one renders two handles with the same key at the same position.
 * First occurrence wins, so the order the edges were made in is kept.
 */
export function edgeDerivedInputHandles(edges: Edge[], nodeId: string): string[] {
  const seen = new Set<string>();
  const handles: string[] = [];
  for (const edge of edges) {
    if (edge.target !== nodeId) continue;
    const handle = edge.targetHandle;
    if (!handle || handle === DEFAULT_INPUT_HANDLE || seen.has(handle)) continue;
    seen.add(handle);
    handles.push(handle);
  }
  return handles;
}

/**
 * The inputs of a Custom SQL node, one per target handle, under the aliases its
 * query runs with. The workflow runner fills one input per handle, a later edge
 * into the same handle replacing an earlier one (so of an If's two branches the
 * live one wins), then renumbers the connected handles from 1 in sorted order:
 * with only handles 2 and 3 wired, the query reads `input_1` and `input_2`.
 */
export function sqlInputsByHandle<E extends { targetHandle?: string | null }>(
  edges: E[]
): Array<{ handle: string; edge: E; alias: string }> {
  const byHandle = new Map<string, E>();
  for (const edge of edges) byHandle.set(edge.targetHandle || "input_layer_1_id", edge);
  return [...byHandle]
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([handle, edge], index) => ({ handle, edge, alias: `input_${index + 1}` }));
}
