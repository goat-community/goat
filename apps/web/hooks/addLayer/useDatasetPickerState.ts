"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useSpaces } from "@/lib/api/content";
import type { ContentQueryParams, Space } from "@/lib/validations/content";

import type {
  ActiveScope,
  ContentLayout,
  ContentOrder,
  ContentOrderBy,
} from "@/hooks/dashboard/content/useContentPageState";
import { LAYOUT_STORAGE_KEY, scopeFeedParams } from "@/hooks/dashboard/content/useContentPageState";
import { useDebouncedValue } from "@/hooks/dashboard/home/useDebouncedValue";

/** What the picker lists by default: folders to navigate, datasets and
 * bundles to pick. */
export const PICKER_TYPES = "folder,layer,bundle";
export const PICKER_PAGE_SIZE = 50;
const SEARCH_DEBOUNCE_MS = 200;

type PickerView = "shared_with_me" | "recent";

const readStoredLayout = (): ContentLayout => {
  if (typeof window === "undefined") return "grid";
  try {
    return window.localStorage.getItem(LAYOUT_STORAGE_KEY) === "list" ? "list" : "grid";
  } catch {
    return "grid";
  }
};

const writeStoredLayout = (layout: ContentLayout): void => {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(LAYOUT_STORAGE_KEY, layout);
  } catch {
    // Storage refused the write: the choice holds for this dialog only.
  }
};

export type DatasetPickerState = {
  active: ActiveScope;
  folderId: string | null;
  goSpace: (spaceId: string) => void;
  goFolder: (folderId: string | null) => void;
  /** Enters a folder that lives in another space — a folder shortcut, or a
   * folder listed by a cross-space view. Scope and folder move together, so
   * the feed is never asked for a folder the active space does not hold. */
  goFolderIn: (spaceId: string, folderId: string) => void;
  goView: (view: PickerView) => void;
  search: string;
  setSearch: (value: string) => void;
  orderBy: ContentOrderBy;
  order: ContentOrder;
  setSort: (orderBy: ContentOrderBy, order: ContentOrder) => void;
  layout: ContentLayout;
  setLayout: (layout: ContentLayout) => void;
  /** Asks the feed for the next `PICKER_PAGE_SIZE` items. The page size
   * stays fixed — the feed caps it — so the host accumulates the pages it
   * has already listed rather than re-reading them. */
  loadMore: () => void;
  spaces: Space[];
  spacesLoading: boolean;
  feedParams: ContentQueryParams | null;
  /** Which collection is being listed — the view, space, folder and search,
   * but not the sort or the page, which only rearrange or extend the same
   * collection. A host holding loaded pages reads this to tell a refetch of
   * the same collection from a move to another one. */
  scopeKey: string;
};

/**
 * The Content page's browsing state, held in memory for a picker: the same
 * scope, folder, search, sort and layout, but nothing touches the URL — a
 * picker runs in a dialog over a project and must not rewrite its address.
 * Layout is shared with the Content page through the same storage key.
 *
 * `types` narrows what the feed is asked for, so a host that cannot use a
 * kind never sees it offered.
 */
export const useDatasetPickerState = ({
  types = PICKER_TYPES,
}: { types?: string } = {}): DatasetPickerState => {
  const { spaces, isLoading: spacesLoading } = useSpaces();
  const personalSpaceId = spaces.find((space) => space.kind === "personal")?.id ?? null;

  const [active, setActive] = useState<ActiveScope>({ kind: "space", spaceId: null });
  const [folderId, setFolderId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [orderBy, setOrderBy] = useState<ContentOrderBy>("updated_at");
  const [order, setOrder] = useState<ContentOrder>("descendent");
  const [layout, setLayoutState] = useState<ContentLayout>(readStoredLayout);

  // Land in the personal space once the spaces are known.
  useEffect(() => {
    if (active.kind === "space" && active.spaceId === null && personalSpaceId) {
      setActive({ kind: "space", spaceId: personalSpaceId });
    }
  }, [active, personalSpaceId]);

  const goSpace = useCallback((spaceId: string) => {
    setActive({ kind: "space", spaceId });
    setFolderId(null);
  }, []);
  const goFolder = useCallback((next: string | null) => setFolderId(next), []);
  const goFolderIn = useCallback((spaceId: string, next: string) => {
    setActive({ kind: "space", spaceId });
    setFolderId(next);
  }, []);
  const goView = useCallback((view: PickerView) => {
    setActive({ kind: "view", view });
    setFolderId(null);
  }, []);
  const setSort = useCallback((by: ContentOrderBy, dir: ContentOrder) => {
    setOrderBy(by);
    setOrder(dir);
  }, []);
  const setLayout = useCallback((next: ContentLayout) => {
    setLayoutState(next);
    writeStoredLayout(next);
  }, []);

  const debouncedSearch = useDebouncedValue(search, SEARCH_DEBOUNCE_MS);

  const scopeParams = useMemo<ContentQueryParams | null>(() => {
    const base = {
      order_by: orderBy,
      order,
      types,
      ...(debouncedSearch ? { search: debouncedSearch } : {}),
    };
    const scope = scopeFeedParams(active, folderId);
    return scope ? { ...scope, ...base } : null;
  }, [active, folderId, debouncedSearch, orderBy, order, types]);

  const scopeKey = useMemo(
    () =>
      JSON.stringify(
        active.kind === "view"
          ? { view: active.view, search: debouncedSearch }
          : { space: active.spaceId, folder: folderId, search: debouncedSearch }
      ),
    [active, folderId, debouncedSearch]
  );

  // Which page of the feed is being asked for. "Load more" advances it at a
  // fixed `size`: the content endpoint caps `size` at 100, so a request that
  // grew the size instead would 422 from the third page on and leave the
  // rest of a large space unreachable.
  const [page, setPage] = useState(1);

  // Anything the feed is asked for anew starts at the first page again —
  // another scope, but a new sort as well. Adjusted during the render that
  // brings the change in rather than in an effect afterwards: React
  // re-renders before committing, so the feed is never keyed on the old page
  // under the new params and no throwaway request goes out.
  const paramsKey = scopeParams ? JSON.stringify(scopeParams) : null;
  const [renderedParamsKey, setRenderedParamsKey] = useState(paramsKey);
  if (renderedParamsKey !== paramsKey) {
    setRenderedParamsKey(paramsKey);
    setPage(1);
  }

  const loadMore = useCallback(() => setPage((prev) => prev + 1), []);

  const feedParams = useMemo<ContentQueryParams | null>(
    () => (scopeParams ? { ...scopeParams, page, size: PICKER_PAGE_SIZE } : null),
    [scopeParams, page]
  );

  return {
    active,
    folderId,
    goSpace,
    goFolder,
    goFolderIn,
    goView,
    search,
    setSearch,
    orderBy,
    order,
    setSort,
    layout,
    setLayout,
    loadMore,
    spaces,
    spacesLoading,
    feedParams,
    scopeKey,
  };
};
