import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("@/lib/api/processes", () => ({ useJobs: () => ({ mutate: vi.fn() }) }));
// useShareNotice's dependencies — no notice fixtures needed for this flow's tests.
vi.mock("@/lib/api/projects", () => ({ useProject: () => ({ project: undefined, isLoading: false }) }));
vi.mock("@/lib/api/teams", () => ({ useTeams: () => ({ teams: [], isLoading: false }) }));
vi.mock("@/hooks/store/ContextHooks", () => ({
  useAppDispatch: () => vi.fn(),
  useAppSelector: () => [],
}));

const created: unknown[] = [];
vi.mock("@/lib/api/layers", () => ({
  createEmptyLayer: (payload: unknown) => {
    created.push(payload);
    return Promise.resolve({ jobID: "job-1" });
  },
}));

import { useCreateFlow } from "@/hooks/addLayer/useCreateFlow";

describe("useCreateFlow", () => {
  it("is a single view with a create action", () => {
    const { result } = renderHook(() => useCreateFlow({ projectId: "p1" }));
    expect(result.current.action.label).toBe("create_layer");
  });

  it("starts on point geometry with one seeded field", () => {
    const { result } = renderHook(() => useCreateFlow({ projectId: "p1" }));
    expect(result.current.create.geometry).toBe("point");
    expect(result.current.create.fields).toHaveLength(1);
    // Seeded field is selected, so the editor opens on something.
    expect(result.current.create.selectedFieldId).toBe(result.current.create.fields[0].id);
  });

  it("maps the table choice to no geometry", () => {
    const { result } = renderHook(() => useCreateFlow({ projectId: "p1" }));
    act(() => result.current.create.setGeometry("table"));
    expect(result.current.create.geometry).toBe("table");
  });

  it("cannot act without a project, and says why", () => {
    const { result } = renderHook(() => useCreateFlow({}));
    expect(result.current.action.disabled).toBe(true);
    expect(result.current.action.reason).toBe("create_layer_needs_project");
  });

  it("sends kinds rather than storage types, and drops computed ones", async () => {
    created.length = 0;
    const { result } = renderHook(() => useCreateFlow({ projectId: "p1" }));
    act(() =>
      result.current.create.setFields([
        { id: "1", name: "label", kind: "string", is_computed: false, display_config: {} },
        { id: "2", name: "seen_at", kind: "datetime", is_computed: false, display_config: {} },
        { id: "3", name: "ok", kind: "boolean", is_computed: false, display_config: {} },
        // Not creatable: its values come from field_config, written only for a layer
        // that already exists.
        { id: "4", name: "size", kind: "area", is_computed: true, display_config: {} },
      ])
    );
    await act(async () => {
      await result.current.action.run();
    });
    expect(created).toHaveLength(1);
    expect(created[0]).toMatchObject({
      geometry_type: "point",
      fields: [
        { name: "label", kind: "string" },
        { name: "seen_at", kind: "datetime" },
        { name: "ok", kind: "boolean" },
      ],
    });
  });

  it("creates serial and uuid fields, a serial with its start", async () => {
    created.length = 0;
    const { result } = renderHook(() => useCreateFlow({ projectId: "p1" }));
    act(() =>
      result.current.create.setFields([
        { id: "1", name: "vorhaben_id", kind: "serial", is_computed: false, display_config: {}, start: 1000 },
        { id: "2", name: "nr", kind: "serial", is_computed: false, display_config: {} },
        { id: "3", name: "uid", kind: "uuid", is_computed: false, display_config: {} },
      ])
    );
    await act(async () => {
      await result.current.action.run();
    });
    const { fields } = created[0] as { fields: Record<string, unknown>[] };
    expect(fields).toEqual([
      { name: "vorhaben_id", kind: "serial", start: 1000 },
      // No start: the server's default (1) applies.
      { name: "nr", kind: "serial" },
      { name: "uid", kind: "uuid" },
    ]);
  });
});
