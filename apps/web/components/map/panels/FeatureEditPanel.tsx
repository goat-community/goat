import { Button, Stack, Typography } from "@mui/material";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";

import TemporalPicker from "@p4b/ui/components/TemporalPicker";

import { useDayjsLocale } from "@/i18n/utils";

import { useDraw } from "@/lib/providers/DrawProvider";
import {
  commitFeature,
  markForDeletion,
  pushSnapshot,
  removePendingFeature,
  setMode,
  updatePendingGeometry,
  updatePendingProperties,
} from "@/lib/store/featureEditor/slice";
import { fieldEditability, selectedVocabularyItem } from "@/lib/utils/allowedValues";
import { BOOLEAN_SELECT_ITEMS, booleanToSelectValue, parseBooleanInput } from "@/lib/utils/fieldInput";
import { formatFieldValue } from "@/lib/utils/formatFieldValue";
import type { FieldKind } from "@/lib/validations/layer";
import { resolveDisplayKind } from "@/lib/validations/layer";

import useLayerFields from "@/hooks/map/CommonHooks";
import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import Container from "@/components/map/panels/Container";
import Selector from "@/components/map/panels/common/Selector";
import SelectorFreeSolo from "@/components/map/panels/common/SelectorFreeSolo";
import TextFieldInput from "@/components/map/panels/common/TextFieldInput";

const FeatureEditPanel: React.FC = () => {
  const dayjsLocale = useDayjsLocale();
  const { t } = useTranslation("common");
  const dispatch = useAppDispatch();
  const { drawControl } = useDraw();
  const { activeLayerId, activeFeatureId, pendingFeatures, mode, geometryType } = useAppSelector(
    (state) => state.featureEditor
  );
  const isTableLayer = !geometryType;
  const { layerFields } = useLayerFields(activeLayerId || "");

  const pushHistory = () => {
    // Snapshot capture must never block the edit itself: getAll() throws when
    // the draw control has been removed from the map.
    let drawFeatures: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [] };
    try {
      drawFeatures = drawControl?.getAll() ?? drawFeatures;
    } catch {
      // fall through with an empty collection
    }
    dispatch(pushSnapshot({ drawFeatures }));
  };

  const filteredFields = layerFields.filter(
    (f) => f.type === "string" || f.type === "number" || f.type === "date" || f.type === "boolean"
  );

  // Track which fields have had a snapshot pushed (reset on feature change)
  const snapshotPushedFieldsRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    snapshotPushedFieldsRef.current.clear();
  }, [activeFeatureId]);

  // Show panel in draw mode or when a feature is selected
  if (!activeLayerId) return null;
  if (mode === "select" && !activeFeatureId) return null;

  const feature = activeFeatureId ? pendingFeatures[activeFeatureId] : null;
  const hasGeometry = feature?.geometry !== null && feature?.geometry !== undefined;

  // For update features, check if anything actually changed
  const hasChanges = (() => {
    if (!feature) return false;
    // For table layers, new features are always committable (no geometry needed)
    // For geospatial layers, require geometry to be drawn
    if (feature.action === "create") return isTableLayer || hasGeometry;
    // Compare geometry and properties with originals
    const geomChanged = JSON.stringify(feature.geometry) !== JSON.stringify(feature.originalGeometry);
    const filterInternal = (props: Record<string, unknown>) => {
      const f = { ...props };
      delete f._fillColor;
      delete f._fillOpacity;
      return f;
    };
    const propsChanged =
      JSON.stringify(filterInternal(feature.properties)) !==
      JSON.stringify(filterInternal(feature.originalProperties || {}));
    return geomChanged || propsChanged;
  })();

  const handlePropertyChange = (fieldName: string, value: string) => {
    if (!activeFeatureId || !feature) return;

    // Push snapshot on first change per field
    if (!snapshotPushedFieldsRef.current.has(fieldName)) {
      snapshotPushedFieldsRef.current.add(fieldName);
      pushHistory();
    }

    const fieldType = filteredFields.find((f) => f.name === fieldName)?.type;
    const parsedValue =
      fieldType === "number"
        ? value === ""
          ? null
          : Number(value)
        : fieldType === "boolean"
          ? parseBooleanInput(value)
          : value || null;
    dispatch(
      updatePendingProperties({
        id: activeFeatureId,
        properties: { ...feature.properties, [fieldName]: parsedValue },
      })
    );
  };

  // A table layer has no tool to stay armed with: its draw mode *is* the one
  // blank row being filled in, added on the way into that mode. So a finished
  // or discarded row ends it, which is also what leaves the toolbar's "Add
  // row" — its only mode button — able to arm the next one. A geospatial layer
  // keeps drawing: there the mode is the user's choice.
  const leaveTableDrawMode = () => {
    if (isTableLayer && mode === "draw") dispatch(setMode("select"));
  };

  const handleDone = () => {
    if (!activeFeatureId || !feature) return;
    // Remove from MapboxDraw — committed features render via GeoJSON overlay
    if (feature.drawFeatureId && drawControl) {
      const drawFeature = drawControl.get(feature.drawFeatureId);
      if (drawFeature?.geometry) {
        dispatch(updatePendingGeometry({ id: activeFeatureId, geometry: drawFeature.geometry }));
      }
      drawControl.delete(feature.drawFeatureId);
    }
    pushHistory();
    // Committing clears the selection, which is what re-arms drawing on a
    // geospatial layer: the mode is left alone there, so finishing one feature
    // leaves the user ready for the next without picking the tool up again.
    dispatch(commitFeature(activeFeatureId));
    leaveTableDrawMode();
  };

  const handleCancel = () => {
    if (activeFeatureId) {
      if (feature?.drawFeatureId && drawControl) {
        drawControl.delete(feature.drawFeatureId);
      }
      dispatch(removePendingFeature(activeFeatureId));
    }
    // On a geospatial layer the mode is the user's choice, not this button's:
    // discarding a shape while drawing leaves them drawing.
    leaveTableDrawMode();
  };

  const handleDelete = () => {
    if (!activeFeatureId || !feature) return;
    if (feature.drawFeatureId && drawControl) {
      drawControl.delete(feature.drawFeatureId);
    }
    pushHistory();
    if (feature.action === "update") {
      dispatch(markForDeletion(activeFeatureId));
    } else {
      dispatch(removePendingFeature(activeFeatureId));
    }
  };

  return (
    <Container
      title={t("feature_attributes")}
      close={handleCancel}
      body={
        <Stack spacing={2}>
          {filteredFields.map((field) => {
            const current = feature?.properties[field.name];
            const {
              computed: isComputed,
              locked: isLocked,
              generated: isGenerated,
              readOnly: isReadOnly,
              vocabulary: isVocabulary,
              suggestions: hasSuggestions,
              items,
            } = fieldEditability(field, current);
            let displayValue = "";
            if (isComputed) {
              if (current != null && current !== "") {
                displayValue = formatFieldValue(
                  current,
                  (resolveDisplayKind(field) as FieldKind) ?? "number",
                  field.display_config ?? {}
                );
              } else if (mode === "draw") {
                displayValue = t("computed_on_save");
              }
            } else if (isLocked) {
              displayValue =
                current != null && current !== "" ? String(current) : mode === "draw" ? t("set_on_save") : "";
            } else {
              displayValue = current != null ? String(current) : "";
            }

            if (isVocabulary) {
              return (
                <Selector
                  key={field.name}
                  label={field.name}
                  enableSearch={items.length > 8}
                  selectedItems={selectedVocabularyItem(items, current)}
                  setSelectedItems={(item) => {
                    const value = Array.isArray(item) ? item[0]?.value : item?.value;
                    handlePropertyChange(field.name, String(value ?? ""));
                  }}
                  items={items}
                />
              );
            }

            // "Allow other values": the vocabulary is offered, and anything
            // else can still be typed.
            if (hasSuggestions) {
              return (
                <SelectorFreeSolo
                  key={field.name}
                  label={field.name}
                  options={items}
                  selectedItem={selectedVocabularyItem(items, current)}
                  inputType={field.type === "number" ? "number" : "text"}
                  commitOnBlur
                  onSelect={(item) => handlePropertyChange(field.name, String(item?.value ?? ""))}
                />
              );
            }

            if (!isReadOnly && field.type === "date") {
              return (
                <TemporalPicker
                  locale={dayjsLocale}
                  key={field.name}
                  kind="datetime"
                  label={field.name}
                  value={(feature?.properties[field.name] as string) ?? ""}
                  onChange={(value) => handlePropertyChange(field.name, value)}
                />
              );
            }

            if (!isReadOnly && field.type === "boolean") {
              const current = booleanToSelectValue(feature?.properties[field.name]);
              return (
                <Selector
                  key={field.name}
                  label={field.name}
                  selectedItems={BOOLEAN_SELECT_ITEMS.find((i) => i.value === current)}
                  setSelectedItems={(item) => {
                    const value = Array.isArray(item) ? item[0]?.value : item?.value;
                    handlePropertyChange(field.name, String(value ?? ""));
                  }}
                  items={[...BOOLEAN_SELECT_ITEMS]}
                />
              );
            }

            return (
              <TextFieldInput
                key={field.name}
                label={field.name}
                type={isReadOnly || field.type !== "number" ? "text" : "number"}
                placeholder={
                  // A new feature has no serial number or UUID until it is
                  // saved; say so rather than showing an empty box.
                  isGenerated
                    ? t("assigned_automatically")
                    : isReadOnly
                      ? ""
                      : field.type === "number"
                        ? t("enter_a_number")
                        : t("enter_text")
                }
                value={displayValue}
                disabled={isReadOnly}
                locked={isLocked || isGenerated}
                tooltip={
                  isGenerated
                    ? t("generated_field_tooltip")
                    : isLocked
                      ? t("field_locked_tooltip")
                      : undefined
                }
                onChange={(value) => {
                  if (isReadOnly) return;
                  handlePropertyChange(field.name, value);
                }}
                clearable={false}
              />
            );
          })}
        </Stack>
      }
      action={
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ width: "100%" }}>
          {feature?.committed || feature?.action === "update" ? (
            <Button
              variant="text"
              size="small"
              color="error"
              onClick={handleDelete}
              sx={{ textTransform: "none" }}>
              {t("delete")}
            </Button>
          ) : (
            <Typography variant="caption" color="text.secondary">
              {/* A table layer has no geometry to draw, and its rows are
                  saveable as soon as they are created — the empty caption
                  stays so the Done button keeps its place in the row. */}
              {!isTableLayer && !hasGeometry ? t("draw_geometry_first") : ""}
            </Typography>
          )}
          <Button
            variant="contained"
            size="small"
            disabled={!hasChanges}
            onClick={handleDone}
            sx={{ textTransform: "none", minWidth: 80 }}>
            {t("done")}
          </Button>
        </Stack>
      }
    />
  );
};

export default FeatureEditPanel;
