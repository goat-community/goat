import { Stack, Typography, useTheme } from "@mui/material";
import { useMemo } from "react";
import { Trans } from "react-i18next";
import type { TooltipProps } from "recharts";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { NameType, ValueType } from "recharts/types/component/DefaultTooltipContent";

import { useTranslation } from "@/i18n/client";

import { useProjectLayerHistogramStats } from "@/lib/api/projects";
import { formatNumber } from "@/lib/utils/format-number";
import type { HistogramStatsQueryParams } from "@/lib/validations/project";
import { histogramStatsQueryParams } from "@/lib/validations/project";
import type { HistogramChartSchema } from "@/lib/validations/widget";
import { histogramChartConfigSchema } from "@/lib/validations/widget";

import { useChartWidget } from "@/hooks/map/DashboardBuilderHooks";

import { ChartStatusContainer } from "@/components/builder/widgets/chart/ChartStatusContainer";
import { StaleDataLoader } from "@/components/builder/widgets/chart/StaleDataLoader";

const CustomTooltip = ({ active, payload }: TooltipProps<ValueType, NameType>) => {
  const { t } = useTranslation("common");
  if (active) {
    return (
      <Stack>
        <Typography variant="caption" fontWeight="bold">
          {`[${payload?.[0]?.payload.range[0]} - ${payload?.[0]?.payload.range[1]}]`}
        </Typography>
        <Typography variant="body2" fontWeight="bold">
          {`${t("count")}: ${payload?.[0]?.payload.count}`}
        </Typography>
      </Stack>
    );
  }
  return null;
};

export const HistogramChartWidget = ({ config: rawConfig }: { config: HistogramChartSchema }) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation("common");
  const { config, queryParams, projectId } = useChartWidget(
    rawConfig,
    histogramChartConfigSchema,
    histogramStatsQueryParams
  );
  const { histogramStats, isLoading, isError } = useProjectLayerHistogramStats(
    projectId,
    config?.setup?.layer_project_id,
    queryParams as HistogramStatsQueryParams
  );
  // Memoized chart data
  const chartData = useMemo(() => histogramStats?.bins || [], [histogramStats]);
  return (
    <>
      <ChartStatusContainer
        config={config}
        queryParams={queryParams}
        isLoading={isLoading && !histogramStats && !isError}
        isError={isError}
      />

      {config && histogramStats && !isError && (
        <ResponsiveContainer width="100%" aspect={1.2}>
          <BarChart data={chartData} margin={{ top: 10, right: 20, bottom: 10 }}>
            {/* Optimized XAxis */}
            <XAxis
              dataKey="range[0]"
              type="number"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(value) => formatNumber(value, config.options?.format, i18n.language)}
              tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
              tickMargin={5}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "transparent" }}
              wrapperStyle={{
                backgroundColor: theme.palette.background.paper,
                borderColor: theme.palette.divider,
                borderRadius: theme.shape.borderRadius,
                borderStyle: "ridge",
                paddingLeft: "5px",
                paddingRight: "5px",
                paddingTop: "5px",
                paddingBottom: "5px",
              }}
              content={<CustomTooltip />}
            />
            <YAxis
              width={40}
              label={{ position: "left" }}
              axisLine={false}
              tickLine={false}
              tickMargin={10}
              tickFormatter={(value) =>
                new Intl.NumberFormat("en-US", {
                  notation: "compact",
                  compactDisplay: "short",
                }).format(value)
              }
              tick={{
                fontSize: theme.typography.caption.fontSize,
                fontFamily: theme.typography.caption.fontFamily,
                fill: theme.palette.text.secondary,
              }}
            />
            <Bar
              dataKey="count"
              fill={config.options?.color || "#0e58ff"}
              radius={[4, 4, 0, 0]}
              cursor="pointer"
              activeBar={{ fill: config.options?.highlight_color || "#f5b704" }}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
      <StaleDataLoader isLoading={isLoading} hasData={!!histogramStats?.bins?.length} />
      {config && histogramStats && histogramStats.total_rows > 0 && !isError && (
        <Typography variant="caption" align="left" gutterBottom>
          <Trans
            i18nKey="common:all_features_have_column"
            values={{
              nr_features: histogramStats.total_rows,
              column_name: config.setup.column_name,
            }}
            components={{ b: <b /> }}
          />
        </Typography>
      )}
      {config && histogramStats?.total_rows === 0 && config.options.filter_by_viewport && !isError && (
        <Typography variant="caption" align="left" gutterBottom>
          {t("no_features_in_viewport")}
        </Typography>
      )}
      {config && histogramStats?.total_rows === 0 && !config.options.filter_by_viewport && !isError && (
        <Typography variant="caption" align="left" gutterBottom>
          {t("no_features_in_layer")}
        </Typography>
      )}
    </>
  );
};
