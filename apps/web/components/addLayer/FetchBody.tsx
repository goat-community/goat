"use client";

import {
  Autocomplete,
  Box,
  Button,
  Chip,
  IconButton,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  alpha,
  useTheme,
} from "@mui/material";
import bboxOf from "@turf/bbox";
import "maplibre-gl/dist/maplibre-gl.css";
import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { MapRef } from "react-map-gl/maplibre";
import { Layer as MapLayer, Map as MapLibre, Source } from "react-map-gl/maplibre";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { type MirrorValue, getMirrorValues } from "@/lib/api/processes";
import { formatBuffer } from "@/lib/catalog/spatial";

import {
  type AreaMode,
  type FetchFlow,
  type FetchSource,
  OSM_TYPES,
  OVERTURE_GROUPS,
  ROAD_CLASSES,
  type TagFilter,
} from "@/hooks/addLayer/useFetchFlow";
import { useCatalogBasemapStyle } from "@/hooks/catalog/useCatalogBasemapStyle";

import UploadDestinationPill from "@/components/addLayer/UploadDestinationPill";
import CatalogSpatialDialog from "@/components/dashboard/catalog/CatalogSpatialDialog";
import DetailMapAttribution from "@/components/dashboard/common/DetailMapAttribution";

const MONO = "ui-monospace, SFMono-Regular, Menlo, monospace";
const SHAPE_COLOR = "#2BB381";

const SectionLabel = ({ children, action }: { children: ReactNode; action?: ReactNode }) => (
  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2, minHeight: 30 }}>
    <Typography
      variant="caption"
      fontWeight={700}
      color="text.secondary"
      sx={{ flex: 1, letterSpacing: 0.6, textTransform: "uppercase" }}>
      {children}
    </Typography>
    {action}
  </Stack>
);

/**
 * One question to the mirror, remembered for the area it was asked about.
 *
 * With `prefetch` it is asked as soon as the area stops changing, and an OSM key list
 * comes in two steps: a quick sample to pick from at once, then the full read with counts.
 */
const useTagOptions = (flow: FetchFlow["fetch"], key?: string, prefetch = false) => {
  const [options, setOptions] = useState<MirrorValue[]>([]);
  const [loading, setLoading] = useState(false);
  const [counting, setCounting] = useState(false);
  const [failed, setFailed] = useState(false);
  const [sampled, setSampled] = useState(false);
  const askedFor = useRef<string | null>(null);
  const question = flow.area ? JSON.stringify([flow.area, flow.source, flow.featureType, key ?? null]) : null;

  const load = useCallback(() => {
    if (!question || !flow.area || askedFor.current === question) return;
    askedFor.current = question;
    const current = question;
    const area = flow.area;
    setLoading(true);
    setFailed(false);
    const ask = (quick: boolean) => getMirrorValues(area, flow.featureType, key, 200, flow.source, quick);
    const full = () =>
      ask(false)
        .then((result) => {
          if (askedFor.current !== current) return;
          setOptions(result.values ?? []);
          setSampled(!!result.sampled);
        })
        .catch((error) => {
          console.error("mirror-values failed", error);
          if (askedFor.current === current) setFailed(true);
        })
        .finally(() => {
          if (askedFor.current !== current) return;
          setLoading(false);
          setCounting(false);
        });
    if (flow.source !== "osm" || key) {
      void full();
      return;
    }
    // One after the other, and the full read only if the area is still the
    // one asked about: a pan would otherwise leave two requests per view
    // running on a server that answers four at a time.
    setCounting(true);
    ask(true)
      .then((result) => {
        if (askedFor.current !== current) return;
        setOptions(result.values ?? []);
        setLoading(false);
        // The quick read saw the whole area: its counts are final.
        if (result.complete) {
          setSampled(false);
          setCounting(false);
          return;
        }
        void full();
      })
      .catch(() => {
        if (askedFor.current === current) void full();
      });
  }, [question, flow.area, flow.featureType, flow.source, key]);
  const latestLoad = useRef(load);
  latestLoad.current = load;

  // Keyed on the question's text alone: the area arrives as a new object on every
  // render, and reacting to that restarted the wait on each re-render and could
  // send the same question twice.
  useEffect(() => {
    askedFor.current = null;
    setOptions([]);
    setSampled(false);
    setCounting(false);
    setLoading(false);
    if (!prefetch || !question) return;
    // The map view changes on every pan; wait until it rests before asking.
    const timer = setTimeout(() => latestLoad.current(), 400);
    return () => clearTimeout(timer);
  }, [question, prefetch]);

  return { options, loading, counting, failed, sampled, load };
};

const AreaSection = ({ flow }: { flow: FetchFlow["fetch"] }) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const [editing, setEditing] = useState<Exclude<AreaMode, "view"> | null>(null);
  const { areaMode, spatial } = flow;

  const modes: { id: AreaMode; label: string }[] = [
    ...(flow.hasMapView ? [{ id: "view" as AreaMode, label: t("fetch_features_area_view") }] : []),
    { id: "region", label: t("catalog_mode_region") },
    { id: "point", label: t("catalog_mode_point") },
    { id: "polygon", label: t("catalog_mode_polygon") },
  ];

  const pick = (mode: AreaMode) => {
    flow.setAreaMode(mode);
    if (mode !== "view" && spatial?.kind !== mode) setEditing(mode);
  };

  const summary =
    areaMode === "view"
      ? null
      : spatial?.kind !== areaMode
        ? t("fetch_features_area_none")
        : spatial.kind === "region"
          ? spatial.nutsIds.map((id) => flow.regionNames[id] ?? id).join(", ")
          : spatial.kind === "point"
            ? `${spatial.label ?? t("catalog_spatial_point")} · ${formatBuffer(spatial.km)}`
            : t("catalog_spatial_area", { count: spatial.ring.length });

  return (
    <Box>
      <SectionLabel>{t("fetch_features_area")}</SectionLabel>
      <Stack
        direction="row"
        role="radiogroup"
        sx={{ borderRadius: 2.5, overflow: "hidden", border: `1.5px solid ${theme.palette.primary.main}` }}>
        {modes.map((mode, index) => (
          <Box
            key={mode.id}
            component="button"
            type="button"
            role="radio"
            aria-checked={mode.id === areaMode}
            onClick={() => pick(mode.id)}
            sx={{
              flex: 1,
              py: 2.5,
              px: 1,
              cursor: "pointer",
              font: "inherit",
              fontSize: 13,
              fontWeight: 600,
              border: "none",
              borderLeft: index > 0 ? `1.5px solid ${theme.palette.primary.main}` : undefined,
              color: theme.palette.primary.main,
              backgroundColor: mode.id === areaMode ? theme.palette.action.selected : "transparent",
            }}>
            {mode.label}
          </Box>
        ))}
      </Stack>
      <Stack
        direction="row"
        spacing={2.5}
        alignItems="center"
        sx={{
          mt: 2.5,
          px: 3,
          py: 2.5,
          borderRadius: 2,
          border: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.action.hover,
        }}>
        <Icon
          iconName={areaMode === "view" ? ICON_NAME.EXPAND : ICON_NAME.LOCATION}
          style={{ fontSize: 14 }}
          htmlColor={theme.palette.primary.main}
        />
        <Typography variant="caption" color="text.secondary" sx={{ flex: 1, lineHeight: 1.45 }}>
          {areaMode === "view" ? t("fetch_features_area_view_hint") : summary}
        </Typography>
        {areaMode !== "view" && (
          <Button size="small" onClick={() => setEditing(areaMode)}>
            {spatial?.kind === areaMode ? t("edit") : t("fetch_features_area_choose")}
          </Button>
        )}
      </Stack>
      <CatalogSpatialDialog
        open={!!editing}
        initial={editing && spatial?.kind === editing ? spatial : null}
        initialMode={editing ?? undefined}
        onClose={() => setEditing(null)}
        onApply={(filter) => {
          flow.setSpatial(filter);
          if (filter) flow.setAreaMode(filter.kind);
          setEditing(null);
        }}
      />
    </Box>
  );
};

const SourceSection = ({ flow }: { flow: FetchFlow["fetch"] }) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const sources: FetchSource[] = ["osm", "overture", "goat"];
  return (
    <Box>
      <SectionLabel>{t("fetch_features_source")}</SectionLabel>
      <Box
        role="radiogroup"
        sx={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 2.5 }}>
        {sources.map((source) => {
          const on = flow.source === source;
          return (
            <Box
              key={source}
              component="button"
              type="button"
              role="radio"
              aria-checked={on}
              onClick={() => flow.setSource(source)}
              sx={{
                textAlign: "left",
                font: "inherit",
                cursor: "pointer",
                p: 3,
                borderRadius: 2.5,
                color: "text.primary",
                border: `1px solid ${on ? theme.palette.primary.main : theme.palette.divider}`,
                boxShadow: on ? `inset 0 0 0 1px ${theme.palette.primary.main}` : "none",
                backgroundColor: on ? alpha(theme.palette.primary.main, 0.06) : "transparent",
              }}>
              <Typography variant="body2" fontWeight={800}>
                {t(`fetch_features_source_${source}`)}
              </Typography>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

const OSM_GEOMETRY: Record<string, "point" | "line" | "polygon"> = {
  points: "point",
  lines: "line",
  multipolygons: "polygon",
};

/** One geometry switch for every source; Overture then offers its themes of that geometry. */
/** The routing network has no feature types or tags: only which road classes to keep. */
const NetworkSection = ({ flow }: { flow: FetchFlow["fetch"] }) => {
  const { t } = useTranslation("common");
  const toggle = (value: string) =>
    flow.setRoadClasses(
      flow.roadClasses.includes(value)
        ? flow.roadClasses.filter((c) => c !== value)
        : [...flow.roadClasses, value]
    );
  return (
    <Box>
      <SectionLabel>{t("fetch_features_road_classes")}</SectionLabel>
      <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1.5}>
        {ROAD_CLASSES.map((value) => {
          const on = flow.roadClasses.includes(value);
          return (
            <Chip
              key={value}
              label={value.replace(/_/g, " ")}
              color={on ? "primary" : "default"}
              variant={on ? "filled" : "outlined"}
              onClick={() => toggle(value)}
              sx={{ fontStyle: "normal", fontWeight: on ? 700 : 500 }}
            />
          );
        })}
      </Stack>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 2, lineHeight: 1.5 }}>
        {t("fetch_features_road_classes_hint")}
      </Typography>
    </Box>
  );
};

const TypeSection = ({ flow }: { flow: FetchFlow["fetch"] }) => {
  const { t } = useTranslation("common");
  const isOsm = flow.source === "osm";
  const group = OVERTURE_GROUPS.find((g) => g.types.includes(flow.overtureType)) ?? OVERTURE_GROUPS[0];
  const geometry = isOsm ? OSM_GEOMETRY[flow.osmType] : group.geometry;

  const pickGeometry = (next: "point" | "line" | "polygon") => {
    if (isOsm) {
      const type = OSM_TYPES.find((candidate) => OSM_GEOMETRY[candidate] === next);
      if (type) flow.setOsmType(type);
    } else {
      const target = OVERTURE_GROUPS.find((g) => g.geometry === next);
      if (target) flow.setOvertureType(target.types[0]);
    }
  };

  return (
    <Box>
      <SectionLabel>{t("fetch_features_type")}</SectionLabel>
      <ToggleButtonGroup
        exclusive
        fullWidth
        size="small"
        color="primary"
        value={geometry}
        onChange={(_, value) => value && pickGeometry(value)}>
        {(["point", "line", "polygon"] as const).map((value) => (
          <ToggleButton key={value} value={value} sx={{ textTransform: "none", fontWeight: 700 }}>
            {t(`fetch_features_geometry_${value}`)}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
      {!isOsm && (
        <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1.5} sx={{ mt: 2.5 }}>
          {group.types.map((type) => {
            const on = flow.overtureType === type;
            return (
              <Chip
                key={type}
                label={t(`fetch_features_type_${type}`)}
                color={on ? "primary" : "default"}
                variant={on ? "filled" : "outlined"}
                onClick={() => flow.setOvertureType(type)}
                sx={{ fontStyle: "normal", fontWeight: on ? 700 : 500 }}
              />
            );
          })}
        </Stack>
      )}
    </Box>
  );
};

const FilterRow = ({
  flow,
  filter,
  keys,
}: {
  flow: FetchFlow["fetch"];
  filter: TagFilter;
  keys: ReturnType<typeof useTagOptions>;
}) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  // Asked as soon as a key is chosen, not when the list opens, so the values are
  // usually there by the time someone clicks.
  const values = useTagOptions(flow, filter.key.trim() || undefined, !!filter.key.trim());
  const counts = useMemo(
    () => Object.fromEntries(values.options.map((option) => [option.value, option.count])),
    [values.options]
  );
  const keyCounts = useMemo(
    () => Object.fromEntries(keys.options.map((option) => [option.value, option.count])),
    [keys.options]
  );
  const keyLabel = t(flow.source === "osm" ? "fetch_features_tag" : "fetch_features_attribute");

  return (
    <Stack direction="row" spacing={1.5} alignItems="flex-start">
      <Stack
        spacing={2.5}
        sx={{ flex: 1, minWidth: 0, p: 3, borderRadius: 2, border: `1px solid ${theme.palette.divider}` }}>
        <Autocomplete
          freeSolo
          size="small"
          options={keys.options.map((option) => option.value)}
          loading={keys.loading}
          onOpen={keys.load}
          value={filter.key}
          onInputChange={(_, next) => flow.updateFilter(filter.id, { key: next, values: [] })}
          renderOption={({ key, ...props }, option) => (
            <li key={key} {...props}>
              <Typography variant="body2" sx={{ flex: 1 }}>
                {option}
              </Typography>
              {/* A placeholder while the counts are read, so the number fills in
                  where it will stand rather than appearing out of nowhere. */}
              {keys.counting ? (
                <Typography variant="caption" color="text.disabled">
                  …
                </Typography>
              ) : (
                !keys.sampled &&
                !!keyCounts[option] && (
                  <Typography variant="caption" color="text.secondary">
                    {keyCounts[option].toLocaleString()}
                  </Typography>
                )
              )}
            </li>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              label={keyLabel}
              helperText={
                keys.failed
                  ? t("osm_tag_failed")
                  : keys.sampled && !keys.counting
                    ? t("fetch_features_reduce_area")
                    : undefined
              }
            />
          )}
        />
        <Autocomplete
          multiple
          freeSolo
          disableCloseOnSelect
          size="small"
          disabled={!filter.key.trim()}
          options={values.options.map((option) => option.value)}
          loading={values.loading}
          onOpen={values.load}
          value={filter.values}
          onChange={(_, next) => flow.updateFilter(filter.id, { values: next as string[] })}
          renderOption={({ key, ...props }, option) => (
            <li key={key} {...props}>
              <Typography variant="body2" sx={{ flex: 1 }}>
                {option}
              </Typography>
              {!values.sampled && !!counts[option] && (
                <Typography variant="caption" color="text.secondary">
                  {counts[option].toLocaleString()}
                </Typography>
              )}
            </li>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              label={t("fetch_features_values")}
              helperText={
                values.failed
                  ? t("osm_tag_failed")
                  : values.sampled
                    ? t("fetch_features_reduce_area")
                    : !filter.values.length && filter.key.trim()
                      ? t("osm_tag_value_optional")
                      : undefined
              }
            />
          )}
        />
      </Stack>
      <IconButton aria-label={t("delete")} onClick={() => flow.removeFilter(filter.id)} sx={{ mt: 4 }}>
        <Icon iconName={ICON_NAME.TRASH} style={{ fontSize: 14 }} />
      </IconButton>
    </Stack>
  );
};

const FilterSection = ({ flow }: { flow: FetchFlow["fetch"] }) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const keys = useTagOptions(flow, undefined, true);
  const isSql = flow.filterMode === "sql";

  const insert = (key: string) => {
    const column = flow.source === "osm" ? `tags['${key}']` : key;
    flow.setSql(flow.sql ? `${flow.sql} ${column}` : column);
  };

  return (
    <Box>
      <SectionLabel
        action={
          <ToggleButtonGroup
            exclusive
            size="small"
            color="primary"
            value={flow.filterMode}
            onChange={(_, value) => value && flow.setFilterMode(value)}>
            <ToggleButton value="builder" sx={{ textTransform: "none", py: 0.5, px: 2.5 }}>
              {t("fetch_features_builder")}
            </ToggleButton>
            <ToggleButton value="sql" sx={{ textTransform: "none", py: 0.5, px: 2.5 }}>
              SQL
            </ToggleButton>
          </ToggleButtonGroup>
        }>
        {t(flow.source === "osm" ? "fetch_features_tag_filters" : "fetch_features_attribute_filters")}
      </SectionLabel>

      {isSql ? (
        <Stack spacing={2.5}>
          <TextField
            multiline
            minRows={5}
            fullWidth
            value={flow.sql}
            onChange={(event) => flow.setSql(event.target.value)}
            placeholder={
              flow.source === "osm"
                ? "tags['amenity'] IN ('school', 'kindergarten')"
                : "categories['primary'] IN ('restaurant', 'cafe')"
            }
            inputProps={{ spellCheck: false, style: { fontFamily: MONO, fontSize: 13 } }}
            InputProps={{
              startAdornment: (
                <Typography
                  component="span"
                  sx={{
                    fontFamily: MONO,
                    fontSize: 12,
                    fontWeight: 700,
                    color: "primary.main",
                    mr: 1.5,
                    alignSelf: "flex-start",
                    pt: 0.25,
                  }}>
                  WHERE
                </Typography>
              ),
            }}
          />
          <Typography variant="caption" color="text.secondary">
            {t(flow.source === "osm" ? "fetch_features_sql_hint_osm" : "fetch_features_sql_hint_overture")}
          </Typography>
          {!!keys.options.length && (
            <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1}>
              {keys.options.slice(0, 16).map((option) => (
                <Chip
                  key={option.value}
                  size="small"
                  variant="outlined"
                  label={option.value}
                  onClick={() => insert(option.value)}
                  sx={{ fontFamily: MONO, fontSize: 11.5 }}
                />
              ))}
            </Stack>
          )}
        </Stack>
      ) : (
        <Stack spacing={2.5}>
          {flow.filters.length > 1 && (
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="body2" color="text.secondary">
                {t("fetch_features_match_prefix")}
              </Typography>
              <ToggleButtonGroup
                exclusive
                size="small"
                color="primary"
                value={flow.match}
                onChange={(_, value) => value && flow.setMatch(value)}>
                <ToggleButton value="all" sx={{ textTransform: "none", py: 0.5, px: 2.5 }}>
                  {t("fetch_features_match_all")}
                </ToggleButton>
                <ToggleButton value="any" sx={{ textTransform: "none", py: 0.5, px: 2.5 }}>
                  {t("fetch_features_match_any")}
                </ToggleButton>
              </ToggleButtonGroup>
            </Stack>
          )}
          {flow.filters.map((filter) => (
            <FilterRow key={filter.id} flow={flow} filter={filter} keys={keys} />
          ))}
          {!flow.filters.length && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ p: 3, borderRadius: 2, backgroundColor: theme.palette.action.hover, lineHeight: 1.5 }}>
              {t("fetch_features_no_filters")}
            </Typography>
          )}
          <Box>
            <Button
              size="small"
              startIcon={<Icon iconName={ICON_NAME.PLUS} style={{ fontSize: 12 }} />}
              onClick={flow.addFilter}>
              {t("fetch_features_add_filter")}
            </Button>
          </Box>
        </Stack>
      )}
    </Box>
  );
};

/** The area on a map. In map-view mode the map is the area, so panning it is how it changes. */
const AreaPreview = ({ flow }: { flow: FetchFlow["fetch"] }) => {
  const { t } = useTranslation("common");
  const basemapStyle = useCatalogBasemapStyle();
  const mapRef = useRef<MapRef | null>(null);
  const isView = flow.areaMode === "view";

  const shape = useMemo<GeoJSON.FeatureCollection>(
    () => ({
      type: "FeatureCollection",
      features: !isView && flow.area ? [{ type: "Feature", geometry: flow.area, properties: {} }] : [],
    }),
    [isView, flow.area]
  );

  useEffect(() => {
    if (isView || !flow.area || !mapRef.current) return;
    const box = bboxOf(shape) as number[];
    mapRef.current.fitBounds([box[0], box[1], box[2], box[3]], { padding: 32, maxZoom: 13, duration: 400 });
  }, [isView, flow.area, shape]);

  return (
    <Box sx={{ position: "relative", flex: 1, minHeight: 280 }}>
      <MapLibre
        id="fetch-features-preview"
        ref={mapRef}
        attributionControl={false}
        initialViewState={
          flow.viewBox
            ? { bounds: flow.viewBox, fitBoundsOptions: { padding: 0 } }
            : { longitude: 10.4, latitude: 51.1, zoom: 4 }
        }
        onMoveEnd={(event) => {
          if (!isView) return;
          const bounds = event.target.getBounds();
          flow.setViewBox([bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()]);
        }}
        style={{ width: "100%", height: "100%" }}
        mapStyle={basemapStyle}>
        <Source id="fetch-area" type="geojson" data={shape}>
          <MapLayer
            id="fetch-area-fill"
            type="fill"
            paint={{ "fill-color": SHAPE_COLOR, "fill-opacity": 0.15 }}
          />
          <MapLayer id="fetch-area-line" type="line" paint={{ "line-color": SHAPE_COLOR, "line-width": 2 }} />
        </Source>
        <DetailMapAttribution />
      </MapLibre>
      <Box
        sx={{
          position: "absolute",
          top: 12,
          left: 12,
          px: 2.5,
          py: 1.5,
          borderRadius: 1.5,
          backgroundColor: "background.paper",
          boxShadow: "0 2px 10px rgba(58,53,65,0.12)",
        }}>
        <Typography variant="caption" fontWeight={700}>
          {isView ? t("fetch_features_area_view_label") : t("fetch_features_area_preview")}
        </Typography>
      </Box>
    </Box>
  );
};

/** Features from map data GOAT hosts, for an area: where, from which source, which ones. */
const FetchBody = ({ controller }: { controller: FetchFlow }) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const { fetch: flow } = controller;

  return (
    <Stack sx={{ minHeight: 0 }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          height: { xs: "auto", md: 560 },
          minHeight: 0,
        }}>
        <Stack
          spacing={5}
          sx={{
            width: { xs: "100%", md: 440 },
            flexShrink: 0,
            p: 5,
            overflowY: "auto",
            borderRight: { md: `1px solid ${theme.palette.divider}` },
          }}>
          <AreaSection flow={flow} />
          <SourceSection flow={flow} />
          {flow.source === "goat" ? (
            <NetworkSection flow={flow} />
          ) : (
            <>
              <TypeSection flow={flow} />
              <FilterSection flow={flow} />
            </>
          )}
        </Stack>
        <AreaPreview flow={flow} />
      </Box>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={4}
        alignItems={{ xs: "stretch", sm: "flex-end" }}
        sx={{ px: 6, pt: 3.5, pb: 4, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Box sx={{ width: { xs: "100%", sm: 400 } }}>
          <Typography
            variant="body2"
            fontWeight="bold"
            component="label"
            htmlFor="fetch-features-name"
            sx={{ display: "block", mb: 1.5 }}>
            {t("layer_name")}
          </Typography>
          <TextField
            id="fetch-features-name"
            fullWidth
            size="small"
            value={flow.name}
            onChange={(event) => flow.setName(event.target.value)}
            error={!flow.name.trim()}
          />
        </Box>
        <Box>
          <Typography variant="body2" fontWeight="bold" sx={{ display: "block", mb: 1.5 }}>
            {t("connect_service_save_to")}
          </Typography>
          <Box sx={{ height: 40, display: "flex", alignItems: "center" }}>
            <UploadDestinationPill
              folders={flow.folders}
              spaces={flow.spaces}
              selected={flow.selectedFolder}
              onSelect={flow.setSelectedFolder}
            />
          </Box>
        </Box>
      </Stack>
    </Stack>
  );
};

export default FetchBody;
