/* eslint-disable @typescript-eslint/no-explicit-any */
import { Box } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { useMap } from "react-map-gl/maplibre";

import { useDatasetCollectionItems } from "@/lib/api/layers";
import type { TemporaryFilter } from "@/lib/store/map/slice";
import { addTemporaryFilter, removeTemporaryFilter, updateTemporaryFilter } from "@/lib/store/map/slice";
import { zoomToFeatureCollection } from "@/lib/utils/map/navigate";
import { type ProjectLayer } from "@/lib/validations/project";
import { type FilterDataSchema, filterLayoutTypes } from "@/lib/validations/widget";

import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import {
  WidgetDataSelector,
  WidgetInfo,
  WidgetOptions,
} from "@/components/builder/widgets/common/WidgetCommonConfigs";
import { WidgetStatusContainer } from "@/components/builder/widgets/common/WidgetStatusContainer";
import SelectorLayerValue from "@/components/map/panels/common/SelectorLayerValue";

// Helper function for deep comparison using JSON.stringify
const areFiltersEqual = (a: TemporaryFilter | undefined, b: TemporaryFilter) => {
  if (!a) return false;
  const cleanA = { ...a, id: undefined }; // Exclude ID from comparison
  const cleanB = { ...b, id: undefined };
  return JSON.stringify(cleanA) === JSON.stringify(cleanB);
};

interface FilterDataProps {
  id: string;
  config: FilterDataSchema;
  projectLayers: ProjectLayer[];
  viewOnly?: boolean;
}

export const FilterDataWidget = ({ id, config: rawConfig, projectLayers }: FilterDataProps) => {
  const dispatch = useAppDispatch();
  const { map } = useMap();
  const [selectedValues, setSelectedValues] = useState<string[] | string | undefined>(
    rawConfig?.setup?.multiple ? [] : ""
  );
  const existingFilter = useAppSelector((state) =>
    state.map.temporaryFilters.find((filter) => filter.id === id)
  );

  const layer = useMemo(() => {
    return projectLayers?.find((l) => l.id === rawConfig?.setup?.layer_project_id) ?? null;
  }, [projectLayers, rawConfig?.setup?.layer_project_id]);

  const geometryDataQueryParams = useMemo(() => {
    const values = Array.isArray(selectedValues) ? selectedValues : [selectedValues];
    if (
      !selectedValues?.length ||
      !rawConfig?.options?.cross_filter ||
      !rawConfig?.setup?.column_name ||
      !layer ||
      layer.feature_layer_geometry_type !== "polygon"
    )
      return undefined;

    return {
      limit: 50,
      offset: 0,
      filter: JSON.stringify({
        op: "or",
        args: values.map((value) => ({
          op: "=",
          args: [{ property: rawConfig.setup.column_name }, value],
        })),
      }),
    };
  }, [selectedValues, rawConfig, layer]);

  const { data: geometryData } = useDatasetCollectionItems(layer?.layer_id || "", geometryDataQueryParams);

  useEffect(() => {
    if (
      !selectedValues ||
      (Array.isArray(selectedValues) && selectedValues.length === 0) ||
      !layer ||
      !rawConfig?.setup?.column_name
    ) {
      if (existingFilter) dispatch(removeTemporaryFilter(id));
      return;
    }

    const normalizedValues = Array.isArray(selectedValues) ? selectedValues : [selectedValues];

    const newFilter: TemporaryFilter = {
      id,
      layer_id: layer.id,
      filter: {
        op: "or",
        args: normalizedValues.map((value) => ({
          op: "=",
          args: [{ property: rawConfig.setup.column_name }, value],
        })),
      },
    };

    if (geometryData && rawConfig?.options?.zoom_to_selection && map) {
      zoomToFeatureCollection(map, geometryData as GeoJSON.FeatureCollection, {
        duration: 200,
      });
    }

    if (geometryData?.features?.length) {
      newFilter.spatial_cross_filter = {
        op: "or",
        args: geometryData.features.map((feature) => ({
          op: "s_intersects",
          args: [{ property: "geom" }, { ...feature.geometry }],
        })),
      };
    }

    // Compare filters using JSON.stringify
    if (!areFiltersEqual(existingFilter, newFilter)) {
      if (existingFilter) {
        dispatch(updateTemporaryFilter(newFilter));
      } else {
        dispatch(addTemporaryFilter(newFilter));
      }
    }
  }, [
    dispatch,
    existingFilter,
    geometryData,
    id,
    layer,
    map,
    rawConfig?.options?.zoom_to_selection,
    rawConfig.setup.column_name,
    selectedValues,
  ]);

  return (
    <Box sx={{ mb: 2 }}>
      <WidgetStatusContainer isNotConfigured={!layer || !rawConfig?.setup?.column_name} height={100} />

      {layer &&
        rawConfig?.setup.column_name &&
        rawConfig?.setup.layout === filterLayoutTypes.Values.select && (
          <SelectorLayerValue
            clearable
            selectedValues={selectedValues as any}
            onSelectedValuesChange={(values: string[] | string | null) => {
              if (values === null || (Array.isArray(values) && values.length === 0)) {
                setSelectedValues(rawConfig?.setup.multiple ? [] : "");
                return;
              }
              setSelectedValues(values as any);
            }}
            layerId={layer.layer_id}
            fieldName={rawConfig?.setup.column_name}
            placeholder={rawConfig?.setup.placeholder}
            multiple={rawConfig?.setup.multiple}
            cqlFilter={layer.query?.cql}
          />
        )}
    </Box>
  );
};

export const FilterDataConfiguration = ({
  config,
  onChange,
}: {
  config: FilterDataSchema;
  onChange: (config: FilterDataSchema) => void;
}) => {
  return (
    <>
      <WidgetInfo
        titleValue={config.setup?.title || ""}
        onTitleChange={(value: string) =>
          onChange({
            ...config,
            setup: {
              ...config.setup,
              title: value,
            },
          })
        }
        hasDescription
        descriptionValue={config.options?.description || ""}
        onDescriptionChange={(value: string) =>
          onChange({
            ...config,
            options: {
              ...config.options,
              description: value,
            },
          })
        }
      />

      <WidgetDataSelector
        projectLayerId={config.setup?.layer_project_id}
        columnName={config.setup?.column_name}
        onProjectLayerIdChange={(layerId: number) => {
          onChange({
            ...config,
            setup: {
              ...config.setup,
              column_name: undefined, // Reset column name when layer changes
              layer_project_id: layerId,
            },
          });
        }}
        onColumnNameChange={(columnName: string | undefined) => {
          onChange({
            ...config,
            setup: {
              ...config.setup,
              column_name: columnName,
            },
          });
        }}
      />

      <WidgetOptions
        sectionLabel="Options"
        hasCrossFilter
        crossFilter={config.options?.cross_filter}
        onCrossFilterChange={(crossFilter: boolean) => {
          onChange({
            ...config,
            options: {
              ...config.options,
              cross_filter: crossFilter,
            },
          });
        }}
        hasZoomToSelection
        zoomToSelection={config.options?.zoom_to_selection}
        onZoomToSelectionChange={(zoomToSelection: boolean) => {
          onChange({
            ...config,
            options: {
              ...config.options,
              zoom_to_selection: zoomToSelection,
            },
          });
        }}
      />
    </>
  );
};
