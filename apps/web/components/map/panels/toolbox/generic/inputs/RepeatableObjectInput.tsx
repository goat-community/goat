/**
 * Repeatable Object Input Component
 *
 * Renders a list of nested object forms with add/remove functionality.
 * Used for array fields with complex object items (e.g., opportunities in heatmap tools).
 */
import { Box, Button, Divider, IconButton, Stack, Typography, useTheme } from "@mui/material";
import { useCallback, useEffect, useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";
import { v4 as uuidv4 } from "uuid";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import {
  defaultFromDependencies,
  formatInputName,
  getDefaultFrom,
  getVisibleInputs,
  resolveDefaultFrom,
} from "@/lib/utils/ogc-utils";

import type { OGCInputSchema, ProcessedInput } from "@/types/map/ogc-processes";

import { GenericInput } from "@/components/map/panels/toolbox/generic/inputs";

interface RepeatableObjectInputProps {
  input: ProcessedInput;
  value: Record<string, unknown>[] | undefined;
  onChange: (value: Record<string, unknown>[] | undefined) => void;
  /** Callback to report filters for nested layer inputs */
  onNestedFiltersChange?: (filters: Record<string, Record<string, unknown> | undefined>[]) => void;
  disabled?: boolean;
  /** Schema definitions ($defs) for resolving $ref */
  schemaDefs?: Record<string, OGCInputSchema>;
  /** All form values for conditional visibility */
  formValues?: Record<string, unknown>;
  /** Map of layer input names to their dataset IDs (for connected layers in workflows) */
  layerDatasetIds?: Record<string, string>;
  /** Map of layer input names to their predicted columns (for connected tool outputs) */
  predictedColumns?: Record<string, Record<string, string>>;
}

/**
 * Process object schema properties into ProcessedInput array
 */
export function processObjectProperties(
  objectSchema: OGCInputSchema,
  schemaDefs?: Record<string, OGCInputSchema>
): ProcessedInput[] {
  const properties = objectSchema.properties || {};
  const requiredFields = objectSchema.required || [];

  const inputs: ProcessedInput[] = [];

  for (const [propName, propSchema] of Object.entries(properties)) {
    // Resolve $ref if present (direct or within anyOf for nullable types)
    let resolvedSchema = propSchema;

    if (propSchema.$ref && schemaDefs) {
      // Direct $ref
      const refName = propSchema.$ref.replace("#/$defs/", "");
      const refSchema = schemaDefs[refName];
      if (refSchema) {
        resolvedSchema = { ...refSchema, ...propSchema, $ref: undefined };
      }
    } else if (propSchema.anyOf && schemaDefs) {
      // anyOf pattern (commonly used for nullable enums: [{"$ref": "..."}, {"type": "null"}])
      const refItem = propSchema.anyOf.find((item) => item.$ref);
      if (refItem?.$ref) {
        const refName = refItem.$ref.replace("#/$defs/", "");
        const refSchema = schemaDefs[refName];
        if (refSchema) {
          // Merge: ref schema provides enum/type, propSchema provides description/x-ui/default
          resolvedSchema = { ...refSchema, ...propSchema, anyOf: undefined };
        }
      }
    }

    const uiMeta = resolvedSchema["x-ui"] || propSchema["x-ui"];
    const isRequired = requiredFields.includes(propName);

    // Infer input type
    let inputType: ProcessedInput["inputType"] = "string";

    if (uiMeta?.widget === "layer-selector") {
      inputType = "layer";
    } else if (uiMeta?.widget === "field-selector" || propName.endsWith("_field")) {
      inputType = "field";
    } else if (uiMeta?.widget === "osm-tag-key" || uiMeta?.widget === "osm-tag-value") {
      inputType = "osm-tag";
    } else if (resolvedSchema.enum) {
      inputType = "enum";
    } else if (resolvedSchema.type === "boolean") {
      inputType = "boolean";
    } else if (resolvedSchema.type === "number" || resolvedSchema.type === "integer") {
      inputType = "number";
    } else if (resolvedSchema.type === "string") {
      inputType = "string";
    } else if (resolvedSchema.type === "array") {
      inputType = "array";
    } else if (resolvedSchema.type === "object") {
      inputType = "object";
    }

    // Extract enum values
    let enumValues: (string | number | boolean)[] | undefined;
    if (resolvedSchema.enum) {
      enumValues = resolvedSchema.enum;
    }

    inputs.push({
      name: propName,
      title: resolvedSchema.title || formatInputName(propName),
      // Prefer the translated x-ui description: only that one honours
      // `description_key`, whereas the raw schema description keeps the
      // field-name translation (same precedence LayerInput uses).
      description: uiMeta?.description ?? resolvedSchema.description,
      inputType,
      required: isRequired,
      schema: resolvedSchema,
      defaultValue: resolvedSchema.default,
      enumValues,
      isLayerInput: uiMeta?.widget === "layer-selector",
      geometryConstraints: uiMeta?.widget_options?.geometry_types as string[] | undefined,
      metadata: [],
      section: uiMeta?.section || "main",
      fieldOrder: uiMeta?.field_order ?? 100,
      uiMeta,
    });
  }

  // Sort by field order
  inputs.sort((a, b) => a.fieldOrder - b.fieldOrder);

  return inputs;
}

/**
 * Get default values for a new object item.
 *
 * `parentValues` are the enclosing form's current values. They let a nested
 * field's `default_by_field` or `default_from` (keyed off parent fields such as
 * `routing_mode` / `cost_type`) resolve when the item is created — otherwise it
 * would silently fall back to the schema default (e.g. a PT opportunity would
 * default to the walking time-limit instead of the PT one).
 */
export function getObjectDefaults(
  objectSchema: OGCInputSchema,
  schemaDefs?: Record<string, OGCInputSchema>,
  parentValues?: Record<string, unknown>
): Record<string, unknown> {
  const defaults: Record<string, unknown> = {};
  const properties = objectSchema.properties || {};

  for (const [propName, propSchema] of Object.entries(properties)) {
    // Resolve $ref if present
    let resolvedSchema = propSchema;
    if (propSchema.$ref && schemaDefs) {
      const refName = propSchema.$ref.replace("#/$defs/", "");
      const refSchema = schemaDefs[refName];
      if (refSchema) {
        resolvedSchema = { ...refSchema, ...propSchema };
      }
    }

    if (resolvedSchema.default !== undefined) {
      defaults[propName] = resolvedSchema.default;
    }

    // default_by_field: derive the initial value from a parent field's value
    // (mirrors getDefaultValues for top-level fields).
    const dbf = (
      resolvedSchema["x-ui"] as
        | { widget_options?: { default_by_field?: { field: string; values: Record<string, unknown> } } }
        | undefined
    )?.widget_options?.default_by_field;
    if (dbf && parentValues) {
      const sourceVal = parentValues[dbf.field];
      if (sourceVal !== undefined && sourceVal !== null) {
        const dynamic = dbf.values[String(sourceVal)];
        if (dynamic !== undefined) defaults[propName] = dynamic;
      }
    }

    // default_from: same purpose, matched across several parent fields at once
    // (e.g. a per-item budget keyed on the parent routing_mode and cost_type).
    if (parentValues) {
      const resolved = resolveDefaultFrom(getDefaultFrom(resolvedSchema), parentValues);
      if (resolved !== undefined) defaults[propName] = resolved;
    }
  }

  return defaults;
}

export default function RepeatableObjectInput({
  input,
  value,
  onChange,
  onNestedFiltersChange,
  disabled,
  schemaDefs,
  formValues = {},
  layerDatasetIds,
  predictedColumns,
}: RepeatableObjectInputProps) {
  const { t } = useTranslation("common");
  const theme = useTheme();

  // Filters for nested layer inputs, keyed itemFilters[itemIndex][layerFieldName].
  // A ref rather than state: nothing here is rendered, it only accumulates so the
  // whole set can be handed to the parent on every change.
  const itemFiltersRef = useRef<Record<number, Record<string, Record<string, unknown> | undefined>>>({});

  // Get item schema (resolve $ref if needed)
  // Handle anyOf pattern for nullable arrays: anyOf: [{type: "array", items: {...}}, {type: "null"}]
  const itemSchema = useMemo(() => {
    let schema = input.schema.items;

    // If items is not at top level, check for anyOf pattern (nullable array)
    if (!schema && input.schema.anyOf) {
      const arrayVariant = input.schema.anyOf.find(
        (v: { type?: string; items?: unknown }) => v.type === "array" && v.items
      );
      if (arrayVariant) {
        schema = arrayVariant.items;
      }
    }

    if (!schema) return null;

    if (schema.$ref && schemaDefs) {
      const refName = schema.$ref.replace("#/$defs/", "");
      return schemaDefs[refName] || schema;
    }
    return schema;
  }, [input.schema.items, input.schema.anyOf, schemaDefs]);

  // Process item properties into input definitions
  const itemInputs = useMemo(() => {
    if (!itemSchema) return [];
    return processObjectProperties(itemSchema, schemaDefs);
  }, [itemSchema, schemaDefs]);

  // Get UI constraints
  const minItems = input.uiMeta?.min_items ?? 0;
  const maxItems = input.uiMeta?.max_items ?? 10;

  // Current items (ensure at least minItems)
  const items = useMemo(() => {
    const currentItems = value || [];
    // Ensure all items have _id for stable keys
    return currentItems.map((item) => ({
      ...item,
      _id: (item as Record<string, unknown>)._id || uuidv4(),
    }));
  }, [value]);

  // Enforce minItems: pad with defaults if current value has fewer items than required
  useEffect(() => {
    if (!itemSchema || minItems <= 0) return;
    const currentLength = value?.length ?? 0;
    if (currentLength < minItems) {
      const defaults = getObjectDefaults(itemSchema, schemaDefs, formValues);
      const padded = [...(value || [])];
      for (let i = currentLength; i < minItems; i++) {
        padded.push({ ...defaults, _id: uuidv4() });
      }
      onChange(padded);
    }
    // onChange excluded: callback identity shouldn't trigger padding
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, minItems, itemSchema, schemaDefs]);

  // Re-resolve nested `default_from` fields when a parent field they depend on
  // changes. Existing items would otherwise keep a value carrying the previous
  // unit (e.g. a 15-minute budget left behind after switching to distance),
  // which then fails validation on submit. Top-level fields get the same
  // treatment in GenericTool.handleInputChange.
  const defaultFromDeps = useMemo(() => {
    const deps: Record<string, unknown> = {};
    for (const i of itemInputs) {
      for (const f of defaultFromDependencies(getDefaultFrom(i.schema))) {
        deps[f] = formValues[f];
      }
    }
    return deps;
  }, [itemInputs, formValues]);
  const depsKey = JSON.stringify(defaultFromDeps);
  const prevDepsKeyRef = useRef(depsKey);

  useEffect(() => {
    if (prevDepsKeyRef.current === depsKey) return;
    prevDepsKeyRef.current = depsKey;
    if (!value?.length) return;
    let changed = false;
    const next = value.map((item) => {
      const updated = { ...item } as Record<string, unknown>;
      for (const i of itemInputs) {
        const resolved = resolveDefaultFrom(getDefaultFrom(i.schema), formValues);
        if (resolved !== undefined && updated[i.name] !== resolved) {
          updated[i.name] = resolved;
          changed = true;
        }
      }
      return updated;
    });
    if (changed) onChange(next);
    // onChange/value excluded: this fires on dependency change, not identity
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [depsKey, itemInputs]);

  // Add new item
  const handleAdd = useCallback(() => {
    if (items.length >= maxItems || !itemSchema) return;
    const defaults = getObjectDefaults(itemSchema, schemaDefs, formValues);
    const newItems = [...items, { ...defaults, _id: uuidv4() }];
    onChange(newItems);
  }, [items, maxItems, itemSchema, schemaDefs, onChange]);

  // Remove item
  const handleRemove = useCallback(
    (index: number) => {
      if (items.length <= minItems) return;
      const newItems = items.filter((_, i) => i !== index);
      onChange(newItems);
    },
    [items, minItems, onChange]
  );

  // Collect layer input names for detecting layer changes and exclusion
  const layerInputNames = useMemo(() => {
    return itemInputs.filter((inp) => inp.inputType === "layer").map((inp) => inp.name);
  }, [itemInputs]);

  // Update item property
  const handleItemChange = useCallback(
    (index: number, propName: string, propValue: unknown) => {
      const newItems = items.map((item, i) => {
        if (i !== index) return item;

        // If changing a layer input, reset all other fields to defaults (except _id)
        const isLayerInput = layerInputNames.includes(propName);
        if (isLayerInput && itemSchema) {
          const defaults = getObjectDefaults(itemSchema, schemaDefs, formValues);
          return {
            ...defaults,
            _id: (item as Record<string, unknown>)._id,
            [propName]: propValue,
          };
        }

        return { ...item, [propName]: propValue };
      });
      onChange(newItems);
    },
    [items, onChange, layerInputNames, itemSchema, schemaDefs]
  );

  // Handle filter change for a nested layer input. The parent is notified from
  // the event handler itself — doing it inside a setState updater would run it
  // during React's render pass and update the parent mid-render.
  const handleItemFilterChange = useCallback(
    (index: number, propName: string, filter: Record<string, unknown> | undefined) => {
      const newFilters = {
        ...itemFiltersRef.current,
        [index]: {
          ...(itemFiltersRef.current[index] || {}),
          [propName]: filter,
        },
      };
      itemFiltersRef.current = newFilters;

      if (onNestedFiltersChange) {
        const filtersArray: Record<string, Record<string, unknown> | undefined>[] = [];
        for (let i = 0; i < items.length; i++) {
          filtersArray.push(newFilters[i] || {});
        }
        onNestedFiltersChange(filtersArray);
      }
    },
    [items.length, onNestedFiltersChange]
  );

  // Get all selected layer IDs across all items for each layer input
  // This prevents selecting the same layer twice across items
  const selectedLayerIdsByInput = useMemo(() => {
    const result: Record<string, string[]> = {};
    for (const layerInputName of layerInputNames) {
      result[layerInputName] = items
        .map((item) => (item as Record<string, unknown>)[layerInputName] as string | undefined)
        .filter((id): id is string => Boolean(id));
    }
    return result;
  }, [items, layerInputNames]);

  if (!itemSchema || itemInputs.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        {t("complex_input_not_supported")}: {input.title}
      </Typography>
    );
  }

  const canAdd = items.length < maxItems;
  const canRemove = items.length > minItems;

  return (
    <Stack spacing={2}>
      {items.map((item, index) => {
        const itemValues = item as Record<string, unknown>;
        // Merge parent form values with item values so visible_when conditions
        const mergedValues = { ...formValues, ...itemValues };
        const visibleInputs = getVisibleInputs(itemInputs, mergedValues);

        // Calculate excluded layer IDs for this item's layer inputs
        // (exclude layers selected in OTHER items, not this item's current selection)
        const getExcludedLayerIds = (inputName: string): string[] => {
          if (!layerInputNames.includes(inputName)) return [];
          const currentValue = itemValues[inputName] as string | undefined;
          return (selectedLayerIdsByInput[inputName] || []).filter((id) => id !== currentValue);
        };

        return (
          <Box key={itemValues._id as string} sx={{ position: "relative" }}>
            {/* Remove button for non-first items */}
            {index > 0 && canRemove && (
              <Stack direction="row" alignItems="center" justifyContent="flex-end" sx={{ mb: 1 }}>
                <IconButton
                  size="small"
                  disabled={disabled}
                  onClick={() => handleRemove(index)}
                  sx={{
                    p: 0.5,
                    "&:hover": {
                      color: theme.palette.error.main,
                    },
                  }}>
                  <Icon htmlColor="inherit" iconName={ICON_NAME.TRASH} style={{ fontSize: "14px" }} />
                </IconButton>
              </Stack>
            )}

            {/* Item fields */}
            <Stack spacing={2}>
              {visibleInputs.map((inputDef) => (
                <GenericInput
                  key={inputDef.name}
                  input={inputDef}
                  value={itemValues[inputDef.name]}
                  onChange={(newValue) => handleItemChange(index, inputDef.name, newValue)}
                  onFilterChange={
                    inputDef.inputType === "layer"
                      ? (filter) => handleItemFilterChange(index, inputDef.name, filter)
                      : undefined
                  }
                  disabled={disabled}
                  formValues={{ ...formValues, ...itemValues }}
                  schemaDefs={schemaDefs}
                  excludedLayerIds={getExcludedLayerIds(inputDef.name)}
                  layerDatasetIds={layerDatasetIds}
                  predictedColumns={predictedColumns}
                />
              ))}
            </Stack>

            {/* Divider between items */}
            {index < items.length - 1 && <Divider sx={{ mt: 2 }} />}
          </Box>
        );
      })}

      {/* Add button */}
      <Divider />
      <Button
        fullWidth
        disabled={disabled || !canAdd}
        onClick={handleAdd}
        variant="text"
        size="small"
        startIcon={<Icon iconName={ICON_NAME.PLUS} style={{ fontSize: "15px" }} />}>
        <Typography variant="body2" color="inherit">
          {t("add")} {formatInputName(input.title.replace(/ies$/i, "y").replace(/s$/i, ""))}
        </Typography>
      </Button>
    </Stack>
  );
}
