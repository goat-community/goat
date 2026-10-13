import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";

import { refreshContentFeed, useSpaces } from "@/lib/api/content";
import { getWritableDestinations, useFolders } from "@/lib/api/folders";
import { executeProcessAsync, useJobs } from "@/lib/api/processes";
import { useProject } from "@/lib/api/projects";
import { useUserProfile } from "@/lib/api/users";
import { type CatalogSpatialFilter, spatialGeometry } from "@/lib/catalog/spatial";
import { addRunningJobIds } from "@/lib/store/jobs/slice";
import type { GetContentQueryParams } from "@/lib/validations/common";
import type { Space } from "@/lib/validations/content";
import type { Folder } from "@/lib/validations/folder";

import type { FlowController } from "@/hooks/addLayer/flow";
import { useShareNotice } from "@/hooks/addLayer/useShareNotice";
import { useCatalogNutsGeometries } from "@/hooks/catalog/useCatalogNutsGeometries";
import { useAppDispatch } from "@/hooks/store/ContextHooks";

export type FetchSource = "osm" | "overture" | "goat";
export type AreaMode = "view" | "region" | "point" | "polygon";
export type FilterMode = "builder" | "sql";
export type MatchMode = "all" | "any";
export type Bbox = [number, number, number, number];
export type TagFilter = { id: number; key: string; values: string[] };

export const OSM_TYPES = ["points", "lines", "multipolygons"] as const;

/** The street network bundle's road classes, as goatlib's ROUTING_CLASSES lists them. */
export const ROAD_CLASSES = [
  "motorway",
  "trunk",
  "primary",
  "secondary",
  "tertiary",
  "residential",
  "living_street",
  "unclassified",
  "service",
  "pedestrian",
  "footway",
  "steps",
  "path",
  "track",
  "cycleway",
  "bridleway",
] as const;

/** Overture's types grouped by the geometry each one yields, as the tool maps them. */
export const OVERTURE_GROUPS: { geometry: "point" | "line" | "polygon"; types: string[] }[] = [
  { geometry: "point", types: ["places", "infrastructure_points"] },
  { geometry: "line", types: ["waterways", "infrastructure_lines"] },
  {
    geometry: "polygon",
    types: ["buildings", "divisions", "land_use", "land", "water_areas", "infrastructure_areas"],
  },
];

const bboxPolygon = ([w, s, e, n]: Bbox): GeoJSON.Polygon => ({
  type: "Polygon",
  coordinates: [
    [
      [w, s],
      [e, s],
      [e, n],
      [w, n],
      [w, s],
    ],
  ],
});

/** Several region outlines become one multipolygon: the tool reads one area. */
const mergePolygons = (geometries: (GeoJSON.Geometry | undefined)[]): GeoJSON.MultiPolygon | undefined => {
  const coordinates: GeoJSON.Position[][][] = [];
  for (const geometry of geometries) {
    if (geometry?.type === "Polygon") coordinates.push(geometry.coordinates);
    if (geometry?.type === "MultiPolygon") coordinates.push(...geometry.coordinates);
  }
  return coordinates.length ? { type: "MultiPolygon", coordinates } : undefined;
};

export type FetchFlowState = {
  areaMode: AreaMode;
  setAreaMode: (mode: AreaMode) => void;
  hasMapView: boolean;
  viewBox?: Bbox;
  setViewBox: (bbox: Bbox) => void;
  spatial: CatalogSpatialFilter | null;
  setSpatial: (filter: CatalogSpatialFilter | null) => void;
  regionNames: Record<string, string>;
  area?: GeoJSON.Polygon | GeoJSON.MultiPolygon;
  source: FetchSource;
  setSource: (source: FetchSource) => void;
  roadClasses: string[];
  setRoadClasses: (classes: string[]) => void;
  osmType: string;
  setOsmType: (type: string) => void;
  overtureType: string;
  setOvertureType: (type: string) => void;
  featureType: string;
  filterMode: FilterMode;
  setFilterMode: (mode: FilterMode) => void;
  match: MatchMode;
  setMatch: (mode: MatchMode) => void;
  filters: TagFilter[];
  addFilter: () => void;
  updateFilter: (id: number, change: Partial<Omit<TagFilter, "id">>) => void;
  removeFilter: (id: number) => void;
  sql: string;
  setSql: (value: string) => void;
  name: string;
  setName: (value: string) => void;
  folders?: Folder[];
  spaces: Space[];
  selectedFolder?: Folder | null;
  setSelectedFolder: (folder: Folder | null) => void;
};

export type FetchFlow = FlowController & { fetch: FetchFlowState };

export const useFetchFlow = ({
  projectId,
  defaultFolderId,
  viewport,
  onDone,
}: {
  projectId?: string;
  defaultFolderId?: string;
  /** The map's bounds when the dialog opened; absent where there is no map. */
  viewport?: Bbox;
  onDone?: () => void;
}): FetchFlow => {
  const { t } = useTranslation("common");
  const dispatch = useAppDispatch();
  const { userProfile } = useUserProfile();
  const { mutate: mutateJobs } = useJobs({ read: false });
  const { project } = useProject(projectId);
  const notice = useShareNotice(projectId);
  const queryParams: GetContentQueryParams = { order: "descendent", order_by: "updated_at" };
  const { folders: allFolders } = useFolders(queryParams);
  const { spaces } = useSpaces();
  const folders = getWritableDestinations(allFolders, spaces);

  const [areaMode, setAreaMode] = useState<AreaMode>(viewport ? "view" : "region");
  const [viewBox, setViewBox] = useState<Bbox | undefined>(viewport);
  const [spatial, setSpatial] = useState<CatalogSpatialFilter | null>(null);
  const [source, setSource] = useState<FetchSource>("osm");
  const [osmType, setOsmType] = useState("points");
  const [overtureType, setOvertureType] = useState("places");
  const [filterMode, setFilterMode] = useState<FilterMode>("builder");
  const [match, setMatch] = useState<MatchMode>("all");
  const [filtersBySource, setFiltersBySource] = useState<Record<FetchSource, TagFilter[]>>({
    osm: [],
    overture: [],
    goat: [],
  });
  const [roadClasses, setRoadClasses] = useState<string[]>([]);
  const [sql, setSql] = useState("");
  const [customName, setCustomName] = useState<string | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>();
  const [isBusy, setIsBusy] = useState(false);
  const nextId = useRef(1);
  const folderInitialized = useRef(false);

  useEffect(() => {
    if (!folders.length || folderInitialized.current) return;
    const initial =
      folders.find((folder) => folder.id === project?.folder_id) ??
      folders.find((folder) => folder.id === defaultFolderId);
    if (initial) {
      setSelectedFolder(initial);
      folderInitialized.current = true;
    }
  }, [folders, project?.folder_id, defaultFolderId]);

  const nutsIds = spatial?.kind === "region" ? spatial.nutsIds : [];
  const { geometries, names } = useCatalogNutsGeometries(nutsIds);
  const regionNames = useMemo(
    () => ({ ...names, ...(spatial?.kind === "region" ? spatial.names : {}) }),
    [names, spatial]
  );

  const area = useMemo(() => {
    if (areaMode === "view") return viewBox ? bboxPolygon(viewBox) : undefined;
    if (!spatial || spatial.kind !== areaMode) return undefined;
    if (spatial.kind === "region") return mergePolygons(spatial.nutsIds.map((id) => geometries[id]));
    return spatialGeometry(spatial);
  }, [areaMode, viewBox, spatial, geometries]);

  const isNetwork = source === "goat";
  const featureType = source === "osm" ? osmType : source === "overture" ? overtureType : "network";
  const filters = filtersBySource[source];
  const setFilters = useCallback(
    (update: (current: TagFilter[]) => TagFilter[]) =>
      setFiltersBySource((all) => ({ ...all, [source]: update(all[source]) })),
    [source]
  );

  const addFilter = useCallback(
    () => setFilters((current) => [...current, { id: nextId.current++, key: "", values: [] }]),
    [setFilters]
  );
  const updateFilter = useCallback(
    (id: number, change: Partial<Omit<TagFilter, "id">>) =>
      setFilters((current) => current.map((f) => (f.id === id ? { ...f, ...change } : f))),
    [setFilters]
  );
  const removeFilter = useCallback(
    (id: number) => setFilters((current) => current.filter((f) => f.id !== id)),
    [setFilters]
  );

  const suggestedName = isNetwork
    ? t("fetch_features_network_default_name")
    : `${t(`fetch_features_source_short_${source}`)} ${t(`fetch_features_type_${featureType}`).toLowerCase()}`;
  const name = customName ?? suggestedName;

  const reset = useCallback(() => {
    setAreaMode(viewport ? "view" : "region");
    setViewBox(viewport);
    setSpatial(null);
    setFiltersBySource({ osm: [], overture: [], goat: [] });
    setRoadClasses([]);
    setSql("");
    setCustomName(null);
    setIsBusy(false);
    setSelectedFolder(undefined);
    folderInitialized.current = false;
  }, [viewport]);

  const usedFilters = filters.filter((f) => f.key.trim());
  const sqlMissing = !isNetwork && filterMode === "sql" && !sql.trim();

  const submit = useCallback(async () => {
    if (!area || !selectedFolder || !name.trim() || sqlMissing) return;
    try {
      setIsBusy(true);
      const job = isNetwork
        ? await executeProcessAsync("street_network_extract", {
            user_id: userProfile?.id,
            project_id: projectId,
            folder_id: selectedFolder.id,
            result_bundle_name: name.trim(),
            area,
            ...(roadClasses.length ? { classes: roadClasses } : {}),
          })
        : await executeProcessAsync("data_integration", {
            user_id: userProfile?.id,
            project_id: projectId,
            folder_id: selectedFolder.id,
            result_layer_name: name.trim(),
            source,
            feature_type: osmType,
            overture_type: overtureType,
            area,
            ...(filterMode === "sql"
              ? { where: sql.trim() }
              : {
                  match_mode: match,
                  tag_filters: usedFilters.map(({ key, values }) => ({ key: key.trim(), values })),
                }),
          });
      if (job?.jobID) {
        mutateJobs();
        dispatch(addRunningJobIds([job.jobID]));
      }
      toast.info(
        t(isNetwork ? "fetch_features_network_started" : "fetch_features_started", { name: name.trim() })
      );
      refreshContentFeed();
      reset();
      onDone?.();
    } catch (error) {
      console.error("fetch features failed", error);
      toast.error(t("error_running_tool"));
      setIsBusy(false);
    }
  }, [
    area,
    selectedFolder,
    name,
    sqlMissing,
    userProfile?.id,
    projectId,
    source,
    isNetwork,
    roadClasses,
    osmType,
    overtureType,
    filterMode,
    sql,
    match,
    usedFilters,
    mutateJobs,
    dispatch,
    t,
    reset,
    onDone,
  ]);

  const reason = !area
    ? t("fetch_features_area_needed")
    : sqlMissing
      ? t("fetch_features_sql_needed")
      : !name.trim()
        ? t("connect_service_name_needed")
        : !selectedFolder
          ? t("connect_service_folder_needed")
          : undefined;

  return {
    isBusy,
    reset,
    action: {
      label: t("add_layer"),
      disabled: !!reason || isBusy,
      reason,
      notice,
      run: submit,
    },
    fetch: {
      areaMode,
      setAreaMode,
      hasMapView: !!viewport,
      viewBox,
      setViewBox,
      spatial,
      setSpatial,
      regionNames,
      area,
      source,
      setSource: (next: FetchSource) => {
        setSource(next);
        setCustomName(null);
      },
      roadClasses,
      setRoadClasses,
      osmType,
      setOsmType: (next: string) => {
        setOsmType(next);
        setCustomName(null);
      },
      overtureType,
      setOvertureType: (next: string) => {
        setOvertureType(next);
        setCustomName(null);
      },
      featureType,
      filterMode,
      setFilterMode,
      match,
      setMatch,
      filters,
      addFilter,
      updateFilter,
      removeFilter,
      sql,
      setSql,
      name,
      setName: setCustomName,
      folders,
      spaces,
      selectedFolder,
      setSelectedFolder,
    },
  };
};
