import * as z from "zod";

import { DEFAULT_COLOR_RANGE } from "@/lib/constants/color";
import { colorRange } from "@/lib/validations/layer";

export const informationTypes = z.enum(["layers"]);
export const chartTypes = z.enum(["histogram_chart", "categories_chart", "pie_chart"]);
export const elementTypes = z.enum(["text", "divider", "image"]);
export const widgetTypes = z.enum([
  ...informationTypes.options,
  ...chartTypes.options,
  ...elementTypes.options,
]);
export const operationTypes = z.enum(["count", "sum", "min", "max"]);
export const sortTypes = z.enum(["asc", "desc"]);

export const formatNumberTypes = z.enum([
  "none", // 1000
  "integer", // 1000 (no commas)
  "comma_separated", // 1,000
  "comma_separated_2d", // 12,345.67
  "signed_2d", // +12,345.67
  "compact", // 1k
  "compact_1d", // 12.3k
  "decimal_2", // 1.23
  "decimal_3", // 1.234
  "decimal_max", // All decimals (up to 3)
  "currency_usd", // $12,345.67
  "currency_eur", // €12,345.67
  "percent", // 1%
  "percent_1d", // 1.0%
  "percent_2d", // 1.00%
]);

// Information configuration schemas
const informationConfigSetupBaseSchema = z.object({
  title: z.string().optional(),
});
const informationConfigOptionsBaseSchema = z.object({});

export const informationConfigSchema = z.object({
  type: informationTypes,
  setup: informationConfigSetupBaseSchema.optional(),
  options: informationConfigOptionsBaseSchema.optional().default({}),
});

export const informationLayersConfigSchema = informationConfigSchema.extend({
  type: z.literal("layers"),
  setup: informationConfigSetupBaseSchema.extend({}),
  options: informationConfigOptionsBaseSchema.extend({
    show_search: z.boolean().optional().default(false),
    open_legend_by_default: z.boolean().optional().default(false),
  }),
});

// Chart configuration schemas
const chartConfigSetupBaseSchema = z.object({
  title: z.string().optional(),
  layer_project_id: z.number().optional(),
});

const chartConfigOptionsBaseSchema = z.object({
  filter_by_viewport: z.boolean().optional().default(true),
  cross_filter: z.boolean().optional().default(true),
  description: z.string().optional(),
});
export const chartsConfigBaseSchema = z.object({
  type: widgetTypes,
  setup: chartConfigSetupBaseSchema.optional(),
  options: chartConfigOptionsBaseSchema.optional().default({}),
});

export const histogramChartConfigSchema = chartsConfigBaseSchema.extend({
  type: z.literal("histogram_chart"),
  setup: chartConfigSetupBaseSchema.extend({
    column_name: z.string().optional(),
  }),
  options: chartConfigOptionsBaseSchema.extend({
    num_bins: z.number().min(1).max(20).optional().default(10),
    min_value: z.number().optional(),
    max_value: z.number().optional(),
    include_outliers: z.boolean().optional().default(false),
    format: formatNumberTypes.optional().default("none"),
    color: z.string().optional().default("#0e58ff"),
    highlight_color: z.string().optional().default("#f5b704"),
  }),
});

export const categoriesChartConfigSchema = chartsConfigBaseSchema.extend({
  type: z.literal("categories_chart"),
  setup: chartConfigSetupBaseSchema.extend({
    expression: z.string().optional(),
  }),
  options: chartConfigOptionsBaseSchema.extend({
    format: formatNumberTypes.optional().default("none"),
    sorting: sortTypes.optional().default("asc"),
    color: z.string().optional().default("#0e58ff"),
    width: z.number().min(3).max(15).optional().default(5),
    num_categories: z.number().min(1).max(15).optional().default(1),
    show_other_aggregate: z.boolean().optional().default(false),
  }),
});

export const pieChartConfigSchema = chartsConfigBaseSchema.extend({
  type: z.literal("pie_chart"),
  setup: chartConfigSetupBaseSchema.extend({
    expression: z.string().optional(),
  }),
  options: chartConfigOptionsBaseSchema.extend({
    num_categories: z.number().min(1).max(15).optional().default(1),
    cap_others: z.boolean().optional().default(false),
    color_range: colorRange.optional().default(DEFAULT_COLOR_RANGE),
  }),
});

// Element configuration schemas
export const textElementConfigSchema = z.object({
  type: z.literal("text"),
  setup: z.object({
    text: z.string().optional(),
  }),
});

export const dividerElementConfigSchema = z.object({
  type: z.literal("divider"),
  setup: z.object({
    color: z.string().optional().default("#000000"),
    size: z.number().min(1).max(10).optional().default(1),
  }),
});

export const imageElementConfigSchema = z.object({
  type: z.literal("image"),
  setup: z.object({
    url: z.string().optional(),
    alt: z.string().optional(),
  }),
});

export type WidgetTypes = z.infer<typeof widgetTypes>;
export type OperationTypes = z.infer<typeof operationTypes>;
export type SortTypes = z.infer<typeof sortTypes>;
export type FormatNumberTypes = z.infer<typeof formatNumberTypes>;
export type HistogramChartSchema = z.infer<typeof histogramChartConfigSchema>;
export type CategoriesChartSchema = z.infer<typeof categoriesChartConfigSchema>;
export type PieChartSchema = z.infer<typeof pieChartConfigSchema>;
export type TextElementSchema = z.infer<typeof textElementConfigSchema>;
export type DividerElementSchema = z.infer<typeof dividerElementConfigSchema>;
export type ImageElementSchema = z.infer<typeof imageElementConfigSchema>;
export type LayerInformationSchema = z.infer<typeof informationLayersConfigSchema>;

export type WidgetChartConfig = HistogramChartSchema | CategoriesChartSchema | PieChartSchema;
export type WidgetElementConfig = TextElementSchema | DividerElementSchema | ImageElementSchema;
export type WidgetInformationConfig = LayerInformationSchema;
