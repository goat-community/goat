/**
 * A tag key or value, offered from the reference area rather than typed.
 *
 * OSM has no fixed schema, so there is no list to hardcode — and a list of every
 * key in the country would be mostly noise. What the chosen area actually holds,
 * with counts, is both the shortest list and the only one that cannot mislead.
 *
 * Free text is still allowed: the mirror holds keys nobody thought to offer.
 */
import { Autocomplete, TextField, Typography } from "@mui/material";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { type OsmTagValue, getOsmTagValues } from "@/lib/api/processes";

import type { ProcessedInput } from "@/types/map/ogc-processes";

import { useFilteredProjectLayers } from "@/hooks/map/LayerPanelHooks";

type OsmTagInputProps = {
  input: ProcessedInput;
  value: unknown;
  onChange: (value: unknown) => void;
  disabled?: boolean;
  /** Merged outer form values and this row's own, so the area and key are here. */
  formValues: Record<string, unknown>;
  /** Layer input name -> dataset id, when the parent already resolved it. */
  layerDatasetIds?: Record<string, string>;
};

const AREA_INPUT = "reference_area_layer_id";

const OsmTagInput = ({ input, value, onChange, disabled, formValues, layerDatasetIds }: OsmTagInputProps) => {
  const { t } = useTranslation("common");
  const { projectId } = useParams();
  const { layers: projectLayers } = useFilteredProjectLayers(projectId as string);
  const [options, setOptions] = useState<OsmTagValue[]>([]);
  const [loading, setLoading] = useState(false);
  // An empty list and a failed call look identical in a dropdown, and the
  // difference is the whole diagnosis: nothing mirrored here, or nothing working.
  const [failed, setFailed] = useState(false);
  const [asked, setAsked] = useState(false);

  const isValueField = input.uiMeta?.widget === "osm-tag-value";
  // The picker stores the *project layer* id (an integer), while the process
  // keys on the dataset UUID -- the same resolution FieldInput does.
  const area = useMemo(() => {
    const resolved = layerDatasetIds?.[AREA_INPUT];
    if (resolved) return resolved;
    const selected = formValues[AREA_INPUT];
    if (typeof selected !== "string" && typeof selected !== "number") return undefined;
    const match = projectLayers?.find(
      (layer) => layer.id === Number(selected) || layer.layer_id === String(selected)
    );
    return match?.layer_id;
  }, [layerDatasetIds, formValues, projectLayers]);
  // Each source names its own kind of feature, and the form shows only the
  // field belonging to the chosen one.
  const source = (formValues["source"] as string) || "osm";
  const featureType =
    source === "overture"
      ? (formValues["overture_type"] as string) || "places"
      : (formValues["feature_type"] as string) || "points";
  // A value list only means something once its key is known.
  const key = isValueField ? (formValues["key"] as string | undefined) : undefined;

  const ready = !!area && (!isValueField || !!key);

  useEffect(() => {
    if (!ready) {
      setOptions([]);
      setAsked(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setFailed(false);
    getOsmTagValues(area as string, featureType, key, 200, source)
      .then((result) => {
        if (cancelled) return;
        setOptions(result.values ?? []);
        setAsked(true);
      })
      .catch((error) => {
        if (cancelled) return;
        console.error("osm-tag-values failed", error);
        setOptions([]);
        setFailed(true);
        setAsked(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ready, area, featureType, key, source]);

  const labels = useMemo(() => options.map((option) => option.value), [options]);
  const counts = useMemo(
    () => Object.fromEntries(options.map((option) => [option.value, option.count])),
    [options]
  );

  const hint = !area
    ? t("osm_tag_needs_area")
    : isValueField && !key
      ? t("osm_tag_needs_key")
      : loading
        ? t("osm_tag_loading")
        : failed
          ? t("osm_tag_failed")
          : asked && !options.length
            ? t("osm_tag_no_data")
            : undefined;

  return (
    <Autocomplete
      freeSolo
      size="small"
      disabled={disabled}
      loading={loading}
      options={labels}
      value={(value as string) ?? ""}
      onChange={(_, next) => onChange(next ?? "")}
      onInputChange={(_, next) => onChange(next)}
      renderOption={(props, option) => (
        <li {...props} key={option}>
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            {option}
          </Typography>
          {/* A column list carries no count — only a value list does. */}
          {!!counts[option] && (
            <Typography variant="caption" color="text.secondary">
              {counts[option].toLocaleString()}
            </Typography>
          )}
        </li>
      )}
      renderInput={(params) => <TextField {...params} label={input.title} helperText={hint} placeholder="" />}
    />
  );
};

export default OsmTagInput;
