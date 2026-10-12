"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import type { ContentQueryParams, ContentType } from "@/lib/validations/content";

export type ContentView = "shared_with_me" | "recent";
export type ActiveScope = { kind: "space"; spaceId: string | null } | { kind: "view"; view: ContentView };

/** The part of a content request that says *which* collection is listed: a
 * cross-space view, or a space and optionally a folder in it. Every surface
 * that lists content (the Content page, the dataset picker) builds its
 * request from this, so they can never ask for a space differently. Null
 * while the space is not yet known. */
export const scopeFeedParams = (
  active: ActiveScope,
  folderId: string | null | undefined
): Pick<ContentQueryParams, "view" | "space_id" | "folder_id"> | null => {
  if (active.kind === "view") return { view: active.view };
  if (!active.spaceId) return null;
  return {
    view: "space",
    space_id: active.spaceId,
    ...(folderId ? { folder_id: folderId } : {}),
  };
};
export type ContentLayout = "grid" | "list";
export type ContentOrderBy = "updated_at" | "created_at" | "name";
export type ContentOrder = "ascendent" | "descendent";

const PAGE_SIZE = 50;
const ALL_TYPES: ContentType[] = ["folder", "project", "layer", "bundle", "template"];

/** What "no type selected" is written as. The key has to stay in the URL to
 * be read back as itself — an empty value is dropped from the query, and an
 * absent `types` means every type — and the word is not a content type, so
 * it filters out to the empty list on the way back in. */
export const NO_TYPES_PARAM = "none";

/** Where grid-vs-list is remembered. Per browser, per person — it says nothing
 * about which content is being looked at, so it is not in the URL. */
export const LAYOUT_STORAGE_KEY = "goat.content.layout";

/** `grid` for anything a browser without usable storage (private mode, storage
 * disabled, a value written by an older build) can give back. */
const readStoredLayout = (): ContentLayout => {
  if (typeof window === "undefined") return "grid";
  try {
    return window.localStorage.getItem(LAYOUT_STORAGE_KEY) === "list" ? "list" : "grid";
  } catch {
    return "grid";
  }
};

/** The personal space's id, kept so the page can name "My content" before the
 * spaces request answers on the next visit. Only ever the caller's own id. */
export const PERSONAL_SPACE_STORAGE_KEY = "goat.content.personalSpaceId";

export const readStoredPersonalSpaceId = (): string | null => {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(PERSONAL_SPACE_STORAGE_KEY);
  } catch {
    return null;
  }
};

export const writeStoredPersonalSpaceId = (spaceId: string): void => {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(PERSONAL_SPACE_STORAGE_KEY, spaceId);
  } catch {
    // Storage refused the write: the next visit shows a placeholder instead.
  }
};

const writeStoredLayout = (layout: ContentLayout): void => {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(LAYOUT_STORAGE_KEY, layout);
  } catch {
    // Storage refused the write: the choice holds for this page only.
  }
};

/** Path segments the cross-space views own. Space ids are UUIDs, so neither
 * word can ever be one — and both have their own route segment, which Next
 * matches before the dynamic `[spaceId]` one. */
export const CONTENT_VIEW_SEGMENT: Record<ContentView, string> = {
  shared_with_me: "shared",
  recent: "recent",
};

/** The address of a content location: `/content/{spaceId}[/{folderId}]` for a
 * space, `/content/shared` or `/content/recent` for a view. */
export const contentPath = (target: { spaceId?: string; folderId?: string; view?: ContentView }): string => {
  if (target.view) return `/content/${CONTENT_VIEW_SEGMENT[target.view]}`;
  if (!target.spaceId) return "/content";
  return target.folderId ? `/content/${target.spaceId}/${target.folderId}` : `/content/${target.spaceId}`;
};

/** Where the route says the page is. Passed down from the route segment that
 * rendered `ContentPage`. */
export type ContentRoute = {
  spaceId?: string;
  folderId?: string;
  view?: ContentView;
};

/**
 * State of the Content page, split by what it means.
 *
 * The browsed location (space/folder or view) is in the URL *path*, so
 * `goSpace`/`goFolder`/`goView` push a new address and the browser's Back
 * button walks the locations.
 *
 * What is being looked for — `q`, `types`, `sort` — is in the query string, so
 * a link carries it. It is written with the native `window.history.replaceState`
 * rather than `router.replace`: Next feeds the native history methods back into
 * `useSearchParams`, so this hook's consumers re-render while the App Router
 * neither refetches the segment nor scrolls. Navigating carries the current
 * query along, so a filtered, sorted list stays filtered and sorted across
 * folders.
 *
 * Grid-vs-list is neither: it is this browser's preference, held in React state
 * and mirrored to `localStorage`, and it never reaches the URL.
 */
export const useContentPageState = ({ spaceId, folderId, view }: ContentRoute = {}) => {
  const router = useRouter();
  const params = useSearchParams();

  const active: ActiveScope = useMemo(
    () => (view ? { kind: "view", view } : { kind: "space", spaceId: spaceId ?? null }),
    [view, spaceId]
  );
  const search = params.get("q") ?? "";
  const types = useMemo(() => {
    const raw = params.get("types");
    // An absent key is every type; `none` — and anything else that names no
    // content type — is the empty selection.
    if (!raw) return ALL_TYPES;
    return raw.split(",").filter((t): t is ContentType => (ALL_TYPES as string[]).includes(t));
  }, [params]);
  const [orderBy, order] = useMemo(() => {
    const [by, dir] = (params.get("sort") ?? "updated_at.desc").split(".");
    const safeBy: ContentOrderBy = by === "name" || by === "created_at" ? by : "updated_at";
    const safeDir: ContentOrder = dir === "asc" ? "ascendent" : "descendent";
    return [safeBy, safeDir] as const;
  }, [params]);

  // Starts at the default so the first client render matches the server-rendered
  // markup, then takes the remembered layout on mount. The feed has no data yet
  // at that point, so what the default frame shows is an empty grid.
  const [layout, setLayoutState] = useState<ContentLayout>("grid");
  useEffect(() => {
    const stored = readStoredLayout();
    if (stored !== "grid") setLayoutState(stored);
  }, []);
  const setLayout = useCallback((next: ContentLayout) => {
    setLayoutState(next);
    writeStoredLayout(next);
  }, []);

  // Links minted by earlier builds carry `?layout=`, which no longer means
  // anything. Dropping it with the history API keeps it out of anything copied
  // from the address bar without costing a navigation.
  useEffect(() => {
    const url = new URL(window.location.href);
    if (!url.searchParams.has("layout")) return;
    url.searchParams.delete("layout");
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
  }, []);

  const update = useCallback(
    (patch: Record<string, string | null>) => {
      const next = new URLSearchParams(params.toString());
      Object.entries(patch).forEach(([k, v]) => (v === null || v === "" ? next.delete(k) : next.set(k, v)));
      const qs = next.toString();
      const path = contentPath({ spaceId, folderId, view });
      window.history.replaceState(null, "", qs ? `${path}?${qs}` : path);
    },
    [params, spaceId, folderId, view]
  );

  // One navigation per location change, always to a whole address — a space
  // and a folder never arrive as two separate writes.
  const goTo = useCallback(
    (target: { spaceId?: string; folderId?: string; view?: ContentView }) => {
      const qs = params.toString();
      const path = contentPath(target);
      router.push(qs ? `${path}?${qs}` : path, { scroll: false });
    },
    [params, router]
  );

  const goSpace = useCallback((id: string) => goTo({ spaceId: id }), [goTo]);
  const goView = useCallback((v: ContentView) => goTo({ view: v }), [goTo]);
  /** A folder of the space currently browsed; `null` goes to its root. */
  const goFolder = useCallback(
    (id: string | null) => {
      if (!spaceId) return;
      goTo({ spaceId, folderId: id ?? undefined });
    },
    [goTo, spaceId]
  );
  /** A folder of any space — a shortcut's target, or a folder listed in one
   * of the cross-space views. */
  const goFolderIn = useCallback(
    (targetSpaceId: string, targetFolderId: string) =>
      goTo({ spaceId: targetSpaceId, folderId: targetFolderId }),
    [goTo]
  );

  const setSearch = useCallback((q: string) => update({ q }), [update]);
  const setTypes = useCallback(
    (next: ContentType[]) =>
      update({
        types: next.length === ALL_TYPES.length ? null : next.length === 0 ? NO_TYPES_PARAM : next.join(","),
      }),
    [update]
  );
  const setSort = useCallback(
    (by: ContentOrderBy, dir: ContentOrder) =>
      update({ sort: `${by}.${dir === "ascendent" ? "asc" : "desc"}` }),
    [update]
  );

  const feedParams: ContentQueryParams | null = useMemo(() => {
    // Nothing can match an empty selection, and the endpoint reads an empty
    // `types` as no filter at all — so the feed is not asked for anything.
    if (types.length === 0) return null;
    const base = {
      size: PAGE_SIZE,
      order_by: orderBy,
      order,
      ...(search ? { search } : {}),
      ...(types.length !== ALL_TYPES.length ? { types: types.join(",") } : {}),
    };
    const scope = scopeFeedParams(active, folderId);
    return scope ? { ...scope, ...base } : null;
  }, [active, folderId, search, types, orderBy, order]);

  return {
    active,
    folderId: folderId ?? null,
    search,
    setSearch,
    types,
    setTypes,
    /** Every type unchecked: the feed is not asked for anything (`feedParams`
     * is null) because nothing can match, and the page says so outright
     * rather than standing blank. Told apart here from the `feedParams` of an
     * unresolved space, which is null too. */
    noTypesSelected: types.length === 0,
    orderBy,
    order,
    setSort,
    layout,
    setLayout,
    goSpace,
    goView,
    goFolder,
    goFolderIn,
    feedParams,
    ALL_TYPES,
  };
};
