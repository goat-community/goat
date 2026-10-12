import { Stack, Typography, useTheme } from "@mui/material";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useProjectLayerAggregationStats } from "@/lib/api/projects";
import { formatNumber } from "@/lib/utils/format-number";
import type { AggregationStatsQueryParams } from "@/lib/validations/project";
import { type ProjectLayer, aggregationStatsQueryParams } from "@/lib/validations/project";
import { type NumbersDataSchema, numbersDataConfigSchema } from "@/lib/validations/widget";

import { useChartWidget } from "@/hooks/map/DashboardBuilderHooks";

import { StaleDataLoader } from "@/components/builder/widgets/common/StaleDataLoader";
import { WidgetStatusContainer } from "@/components/builder/widgets/common/WidgetStatusContainer";

interface NumbersDataProps {
  config: NumbersDataSchema;
  projectLayers: ProjectLayer[];
  viewOnly?: boolean;
}

export const NumbersDataWidget = ({ config: rawConfig }: NumbersDataProps) => {
  const { t, i18n } = useTranslation("common");
  const theme = useTheme();
  const { config, queryParams, layerId, isLayerLocked } = useChartWidget(
    rawConfig,
    numbersDataConfigSchema,
    aggregationStatsQueryParams
  );

  const { aggregationStats, isLoading, isError } = useProjectLayerAggregationStats(
    layerId,
    queryParams as AggregationStatsQueryParams
  );

  const displayValue = useMemo(() => {
    const val = aggregationStats?.items?.[0]?.operation_value;
    return typeof val === "number" ? val : Number(val) || 0;
  }, [aggregationStats]);

  const renderIcon = useMemo(() => {
    const icon = config?.setup?.icon;
    if (!icon) return null;
    // Check if the icon is a URL, absolute or root-relative (the shipped artwork)
    if (
      typeof icon === "string" &&
      (icon.startsWith("http://") || icon.startsWith("https://") || icon.startsWith("/"))
    ) {
      const isSvg = icon.endsWith(".svg");
      return (
        <img
          src={icon}
          alt="icon"
          style={{
            width: 40,
            height: 40,
            ...(isSvg &&
              theme.palette.mode === "dark" && {
                filter: "invert(100%) brightness(200%)", // Makes the SVG white in dark mode
              }),
          }}
        />
      );
    }
    // Check if the icon is included in ICON_NAME
    if (typeof icon === "string" && Object.values(ICON_NAME).includes(icon as ICON_NAME)) {
      return <Icon iconName={icon as ICON_NAME} fontSize="large" />;
    }
    // If the icon is neither a valid URL nor in ICON_NAME, don't render anything
    return null;
  }, [config?.setup?.icon, theme.palette.mode]);

  // D7: `layer_project_id` alone doesn't say whether the layer is locked
  // for this viewer — `isLayerLocked` (from useChartWidget) does, and
  // withholding it here is what shows the locked hint instead of a blank
  // widget (queryParams itself doesn't depend on layerId).
  const isWidgetConfigured = useMemo(() => {
    return config?.setup?.layer_project_id && queryParams && !isLayerLocked;
  }, [config, queryParams, isLayerLocked]);

  return (
    <>
      <WidgetStatusContainer
        isLoading={isLoading && !aggregationStats && !isError}
        isNotConfigured={!isWidgetConfigured}
        isNotConfiguredMessage={isLayerLocked ? t("layer_locked_hint") : undefined}
        isError={isError}
        height={100}
      />

      {config && !isError && aggregationStats && isWidgetConfigured && (
        <Stack direction="row" spacing={4} alignItems="center">
          {renderIcon}
          <Typography variant="h4" fontWeight="bold">
            {formatNumber(displayValue, config.options?.format, i18n.language)}
          </Typography>
        </Stack>
      )}

      <StaleDataLoader isLoading={isLoading} hasData={!!aggregationStats} />
    </>
  );
};
