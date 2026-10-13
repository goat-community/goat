/**
 * Hook for fetching and managing atlas features.
 *
 * Fetches features from the coverage layer when atlas is enabled,
 * applying any CQL filters from the project layer.
 */
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import { useDatasetCollectionItems } from "@/lib/api/layers";
import { generateFeaturePages } from "@/lib/print/atlas-utils";
import type { AtlasPage, AtlasResult } from "@/lib/print/atlas-utils";
import type { ProjectLayer } from "@/lib/validations/project";
import type { AtlasConfig, AtlasFeatureCoverage } from "@/lib/validations/reportLayout";

export interface UseAtlasFeaturesOptions {
  /** Atlas configuration from the report layout */
  atlasConfig?: AtlasConfig;
  /** Project layers to find the coverage layer */
  projectLayers?: ProjectLayer[];
  /** Current atlas page index (0-based) */
  currentPageIndex?: number;
  /** Maximum number of atlas pages (from backend config) */
  atlasMaxPages: number;
}

export interface UseAtlasFeaturesResult {
  /** Whether atlas features are being loaded */
  isLoading: boolean;
  /** Error if fetching failed */
  isError: boolean;
  /** Generated atlas pages */
  atlasResult: AtlasResult | null;
  /** Current atlas page (based on currentPageIndex) */
  currentPage: AtlasPage | null;
  /** Total number of atlas pages */
  totalPages: number;
  /** The coverage layer (project layer) */
  coverageLayer: ProjectLayer | null;
  /** Raw GeoJSON features from the coverage layer */
  features: GeoJSON.Feature[];
  /** Whether features were truncated to the max page limit */
  wasTruncated: boolean;
  /** Total feature count before truncation */
  totalFeatureCount: number;
}


/**
 * Hook for fetching atlas coverage layer features.
 *
 * When atlas is enabled with a feature coverage layer:
 * 1. Finds the coverage layer in projectLayers
 * 2. Fetches all features from that layer using GeoAPI
 * 3. Applies the layer's CQL filter (if any)
 * 4. Generates atlas pages from the features
 *
 * @example
 * ```tsx
 * const { atlasResult, currentPage, isLoading } = useAtlasFeatures({
 *   atlasConfig: reportLayout.config.atlas,
 *   projectLayers,
 *   currentPageIndex: 0,
 * });
 *
 * if (atlasResult) {
 *   console.log(`Atlas has ${atlasResult.totalPages} pages`);
 * }
 * ```
 */
export function useAtlasFeatures({
  atlasConfig,
  projectLayers,
  currentPageIndex = 0,
  atlasMaxPages,
}: UseAtlasFeaturesOptions): UseAtlasFeaturesResult {
  const { t } = useTranslation("common");
  // Find the coverage layer from project layers
  const coverageLayer = useMemo(() => {
    if (!atlasConfig?.enabled || atlasConfig?.coverage?.type !== "feature") {
      return null;
    }

    const featureCoverage = atlasConfig.coverage as AtlasFeatureCoverage;
    return projectLayers?.find((l) => l.id === featureCoverage.layer_project_id) ?? null;
  }, [atlasConfig, projectLayers]);

  // Build query params — uses the layer's own CQL filter if set
  const queryParams = useMemo(() => {
    if (!coverageLayer || !atlasConfig?.enabled) {
      return undefined;
    }

    const layerCqlFilter = coverageLayer.query?.cql;

    return {
      limit: atlasMaxPages,
      offset: 0,
      ...(layerCqlFilter ? { filter: JSON.stringify(layerCqlFilter) } : {}),
    };
  }, [coverageLayer, atlasConfig]);

  // Fetch features from GeoAPI
  const { data, isLoading, isError } = useDatasetCollectionItems(
    coverageLayer?.layer_id || "",
    atlasConfig?.enabled ? queryParams : undefined
  );

  // Convert to GeoJSON features
  const features = useMemo<GeoJSON.Feature[]>(() => {
    if (!data?.features) return [];

    return data.features.map((f) => ({
      type: "Feature" as const,
      id: f.id,
      geometry: f.geometry as GeoJSON.Geometry,
      properties: f.properties as Record<string, unknown>,
    }));
  }, [data]);

  // Generate atlas pages
  const atlasResult = useMemo<AtlasResult | null>(() => {
    if (!atlasConfig?.enabled || atlasConfig?.coverage?.type !== "feature") {
      return null;
    }

    if (features.length === 0) {
      return null;
    }

    const featureCoverage = atlasConfig.coverage as AtlasFeatureCoverage;
    // The default label is shown on the canvas and printed, so it follows the
    // reader's language; the placeholders stay as the template syntax.
    const labelTemplate =
      atlasConfig.page_label?.template ||
      t("atlas_page_label_default", { defaultValue: "Page {page_number} of {total_pages}" });

    // Enforce max page limit
    const effectiveFeatures = features.slice(0, atlasMaxPages);
    return generateFeaturePages(featureCoverage, effectiveFeatures, labelTemplate);
  }, [atlasConfig, features, t]);

  // Get current page
  const currentPage = useMemo<AtlasPage | null>(() => {
    if (!atlasResult?.pages) return null;

    const index = Math.max(0, Math.min(currentPageIndex, atlasResult.pages.length - 1));
    return atlasResult.pages[index] ?? null;
  }, [atlasResult, currentPageIndex]);

  return {
    isLoading,
    isError,
    atlasResult,
    currentPage,
    totalPages: atlasResult?.totalPages ?? 0,
    coverageLayer,
    features,
    wasTruncated: (data?.numberMatched ?? 0) > atlasMaxPages,
    totalFeatureCount: data?.numberMatched ?? 0,
  };
}
