import { Box, Button, Divider, IconButton, Paper, Stack, Typography } from "@mui/material";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Popup } from "react-map-gl/maplibre";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";
import TemporalPicker from "@p4b/ui/components/TemporalPicker";

import { useDayjsLocale } from "@/i18n/utils";

import { fieldEditability, selectedVocabularyItem } from "@/lib/utils/allowedValues";
import { booleanToSelectValue, getBooleanSelectItems, parseBooleanInput } from "@/lib/utils/fieldInput";
import { formatFieldValue } from "@/lib/utils/formatFieldValue";
import type { FieldKind } from "@/lib/validations/layer";
import { resolveDisplayKind } from "@/lib/validations/layer";

import type { MapPopoverEditorProps } from "@/types/map/popover";
import { EditorModes } from "@/types/map/popover";

import useLayerFields from "@/hooks/map/CommonHooks";

import Selector from "@/components/map/panels/common/Selector";
import SelectorFreeSolo from "@/components/map/panels/common/SelectorFreeSolo";
import TextFieldInput from "@/components/map/panels/common/TextFieldInput";

const MapPopoverEditor: React.FC<MapPopoverEditorProps> = ({
  title,
  lngLat,
  onClose,
  onConfirm,
  layer,
  feature,
  editMode,
}) => {
  const { t } = useTranslation("common");
  const dayjsLocale = useDayjsLocale();
  const popup = useMemo(() => {
    if (editMode === EditorModes.DELETE) {
      return {
        title: t("delete_feature"),
        icon: ICON_NAME.TRASH,
        confirmText: t("delete"),
        confirmColor: "error",
      };
    } else if (editMode === EditorModes.MODIFY_ATTRIBUTES) {
      return {
        title: t("modify_attributes"),
        icon: ICON_NAME.EDIT,
        confirmText: t("save"),
        confirmColor: "primary",
      };
    } else if (editMode === EditorModes.DRAW) {
      return {
        title: t("draw_feature"),
        icon: ICON_NAME.PLUS,
        confirmText: t("save"),
        confirmColor: "primary",
      };
    }
  }, [editMode, t]);

  const { layerFields } = useLayerFields(layer?.id || "");
  const filteredLayerFields = useMemo(() => {
    return layerFields.filter(
      (field) =>
        field.type === "string" ||
        field.type === "number" ||
        field.type === "date" ||
        field.type === "boolean"
    );
  }, [layerFields]);

  const [featureProperties, setFeatureProperties] = useState<
    Record<string, string | number | boolean | null>
  >(feature?.properties || {});

  const _lngLat = useMemo(() => {
    let _lngLat = lngLat || [0, 0];
    if (!lngLat && feature?.geometry) {
      const coordinates = feature.geometry["coordinates"];
      if (layer?.feature_layer_geometry_type === "point") {
        _lngLat = coordinates;
      } else if (layer?.feature_layer_geometry_type === "line") {
        const lastCoordinate = coordinates[coordinates.length - 1];
        _lngLat = lastCoordinate;
      } else if (layer?.feature_layer_geometry_type === "polygon") {
        const lastCoordinate = coordinates[0][coordinates[0].length - 1];
        _lngLat = lastCoordinate;
      }
    }
    return _lngLat;
  }, [feature, lngLat, layer?.feature_layer_geometry_type]);

  return (
    <Popup
      onClose={onClose}
      longitude={_lngLat[0]}
      latitude={_lngLat[1]}
      closeButton={false}
      maxWidth="340px">
      <Box>
        <Paper elevation={0}>
          <Stack sx={{ px: 2, pt: 2 }} direction="row" alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={2} alignItems="center" sx={{ width: "100%" }}>
              {popup?.icon && <Icon iconName={popup?.icon} style={{ fontSize: 16 }} />}
              <Typography variant="body2" fontWeight="bold">
                {title || popup?.title}
              </Typography>
            </Stack>
            <IconButton onClick={onClose}>
              <Icon iconName={ICON_NAME.XCLOSE} style={{ fontSize: 16 }} />
            </IconButton>
          </Stack>
          <Divider sx={{ mb: 0 }} />
          <Box sx={{ maxHeight: "280px", overflowY: "auto", overflowX: "hidden" }}>
            {editMode === EditorModes.DELETE && (
              <Stack
                sx={{ pt: 2, px: 2 }}
                direction="row"
                spacing={2}
                alignItems="center"
                justifyContent="center">
                <Typography variant="body2" fontWeight="bold">
                  {t("delete_this_feature")}
                </Typography>
              </Stack>
            )}
            {(editMode === EditorModes.MODIFY_ATTRIBUTES || editMode === EditorModes.DRAW) && (
              <Stack sx={{ pt: 2, px: 2 }} direction="column" spacing={2} minWidth="300px">
                {filteredLayerFields.map((field) => {
                  const current = featureProperties[field.name];
                  // Locked and computed columns are not offered here either —
                  // see FeatureEditPanel. Derived once, in one place.
                  const {
                    computed: isComputed,
                    locked: isLocked,
                    readOnly: isReadOnly,
                    vocabulary: isVocabulary,
                    suggestions: hasSuggestions,
                    items,
                  } = fieldEditability(field, current);
                  const isPicker = isVocabulary || hasSuggestions;
                  let displayValue = "";
                  if (isComputed) {
                    // Format the computed value via the shared formatter so the
                    // user sees the same string they get in the data table.
                    if (current !== undefined && current !== null && current !== "") {
                      displayValue = formatFieldValue(
                        current,
                        (resolveDisplayKind(field) as FieldKind) ?? "number",
                        field.display_config ?? {}
                      );
                    } else if (editMode === EditorModes.DRAW) {
                      displayValue = t("computed_on_save");
                    }
                  } else if (isLocked) {
                    displayValue =
                      current !== null && current !== undefined && current !== ""
                        ? String(current)
                        : editMode === EditorModes.DRAW
                          ? t("set_on_save")
                          : "";
                  } else {
                    displayValue =
                      current !== null && current !== undefined && current !== "" ? String(current) : "";
                  }

                  const setProperty = (value: string | number | undefined) =>
                    setFeatureProperties((prev) => ({
                      ...prev,
                      [field.name]: value === "" || value === undefined ? null : value,
                    }));

                  return (
                    <Stack key={field.name} direction="row" spacing={2} alignItems="center">
                      {isVocabulary && (
                        <Selector
                          label={field.name}
                          enableSearch={items.length > 8}
                          selectedItems={selectedVocabularyItem(items, current)}
                          setSelectedItems={(item) => {
                            const value = Array.isArray(item) ? item[0]?.value : item?.value;
                            setProperty(value);
                          }}
                          items={items}
                        />
                      )}
                      {/* "Allow other values": the vocabulary is a set of
                          suggestions, and anything else can still be typed. */}
                      {hasSuggestions && (
                        <SelectorFreeSolo
                          label={field.name}
                          options={items}
                          selectedItem={selectedVocabularyItem(items, current)}
                          inputType={field.type === "number" ? "number" : "text"}
                          commitOnBlur
                          onSelect={(item) =>
                            setProperty(
                              field.type === "number" && item?.value !== undefined && item.value !== ""
                                ? Number(item.value)
                                : item?.value
                            )
                          }
                        />
                      )}
                      {!isPicker && !isReadOnly && field.type === "date" && (
                        <TemporalPicker
                          locale={dayjsLocale}
                          kind="datetime"
                          label={field.name}
                          value={(featureProperties[field.name] as string) ?? ""}
                          onChange={(value) => {
                            setFeatureProperties((prev) => ({ ...prev, [field.name]: value || null }));
                          }}
                        />
                      )}
                      {!isPicker && !isReadOnly && field.type === "boolean" && (
                        <Selector
                          label={field.name}
                          selectedItems={getBooleanSelectItems(t).find(
                            (i) => i.value === booleanToSelectValue(featureProperties[field.name])
                          )}
                          setSelectedItems={(item) => {
                            const value = Array.isArray(item) ? item[0]?.value : item?.value;
                            setFeatureProperties((prev) => ({
                              ...prev,
                              [field.name]: parseBooleanInput(String(value ?? "")),
                            }));
                          }}
                          items={getBooleanSelectItems(t)}
                        />
                      )}
                      {!isPicker &&
                        (field.type === "string" ||
                          field.type === "number" ||
                          (isReadOnly && (field.type === "date" || field.type === "boolean"))) && (
                          <TextFieldInput
                            type={isReadOnly || field.type !== "number" ? "text" : "number"}
                            label={field.name}
                            clearable={false}
                            disabled={isReadOnly}
                            locked={isLocked}
                            tooltip={isLocked ? t("field_locked_tooltip") : undefined}
                            value={displayValue}
                            onChange={(value: string) => {
                              if (isReadOnly) return;
                              const parsedValue = field.type === "number" ? Number(value) : value;
                              setFeatureProperties((prev) => ({ ...prev, [field.name]: parsedValue }));
                            }}
                          />
                        )}
                    </Stack>
                  );
                })}
              </Stack>
            )}
          </Box>

          <Divider />
          <Stack
            sx={{ pb: 2, px: 2 }}
            direction="row"
            spacing={2}
            alignItems="center"
            justifyContent="flex-end">
            <Button onClick={onClose} variant="text" sx={{ borderRadius: 0 }}>
              <Typography variant="body2" fontWeight="bold">
                {t("cancel")}
              </Typography>
            </Button>
            <Button
              onClick={() => {
                onConfirm(featureProperties);
              }}
              variant="text"
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              color={(popup?.confirmColor as any) || "primary"}
              sx={{ borderRadius: 0 }}>
              <Typography variant="body2" fontWeight="bold" color="inherit">
                {popup?.confirmText}
              </Typography>
            </Button>
          </Stack>
        </Paper>
      </Box>
    </Popup>
  );
};

export default MapPopoverEditor;
