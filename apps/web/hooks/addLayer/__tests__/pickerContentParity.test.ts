/**
 * The dataset picker and the Content page must list a space the same way.
 *
 * Both build their request from `scopeFeedParams`; this pins that, so a rule
 * about what a space contains cannot land in one surface and not the other
 * (as "shared into this space" once did: a Content-page-only merge the
 * picker never saw).
 */
import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useDatasetPickerState } from "@/hooks/addLayer/useDatasetPickerState";
import { scopeFeedParams, useContentPageState } from "@/hooks/dashboard/content/useContentPageState";

const spaces = [
  { id: "p1", kind: "personal", name: "Me" },
  { id: "t1", kind: "team", name: "Team" },
];
vi.mock("@/lib/api/content", () => ({ useSpaces: () => ({ spaces, isLoading: false }) }));
vi.mock("@/hooks/dashboard/home/useDebouncedValue", () => ({ useDebouncedValue: <T>(value: T) => value }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

type Route = { spaceId?: string; folderId?: string; view?: "shared_with_me" | "recent" };

const scopeOf = (params: Record<string, unknown> | null) =>
  params && { view: params.view, space_id: params.space_id, folder_id: params.folder_id };

describe("dataset picker and Content page list a space identically", () => {
  it.each<[string, Route]>([
    ["a team space's root", { spaceId: "t1" }],
    ["a folder in a team space", { spaceId: "t1", folderId: "f1" }],
    ["a view", { view: "shared_with_me" }],
  ])("for %s", (_name, route) => {
    const content = renderHook(() => useContentPageState(route)).result.current.feedParams;
    const picker = renderHook(() => {
      const state = useDatasetPickerState();
      return state;
    });
    if (route.view) picker.result.current.goView(route.view);
    else if (route.folderId) picker.result.current.goFolderIn(route.spaceId as string, route.folderId);
    else picker.result.current.goSpace(route.spaceId as string);
    picker.rerender();
    expect(scopeOf(picker.result.current.feedParams)).toEqual(scopeOf(content));
    // Neither asks for anything the shared function does not say.
    const active = route.view
      ? { kind: "view" as const, view: route.view }
      : { kind: "space" as const, spaceId: route.spaceId as string };
    expect(scopeOf(content)).toEqual(scopeOf(scopeFeedParams(active, route.folderId ?? null)));
  });
});
