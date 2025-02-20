import * as z from "zod";


// Chart Configurations

export const chartTypes = z.enum(["histogram", "categories", "pie_chart"]);
export const widgetTypes = z.enum([...chartTypes.options]);
export const operationTypes = z.enum(["count", "sum", "average", "min", "max"]);
export const sortTypes = z.enum(["asc", "desc"]);


const chartConfigSetupBaseSchema = z.object({
  title: z.string().optional(),
  layer_project_id: z.string().optional(),
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
  type: z.literal("histogram"),
  setup: chartConfigSetupBaseSchema.extend({
    aggregation: z.string().optional(),
  }),
  options: chartConfigOptionsBaseSchema.extend({
    num_bins: z.number().min(1).max(20).optional().default(10),
    min_value: z.number().optional(),
    max_value: z.number().optional(),
    include_outliers: z.boolean().optional().default(false),
    format: z.string().optional(), // Add enum
    color: z.string().optional().default("#0e58ff"),
    highlight_color: z.string().optional().default("#f5b704"),
  })
})


export const categoriesChartConfigSchema = chartsConfigBaseSchema.extend({
  type: z.literal("categories"),
  setup: chartConfigSetupBaseSchema.extend({
    field: z.string().optional(),
    operation: operationTypes.optional(),
    aggregation: z.string().optional(),
  }),
  options: chartConfigOptionsBaseSchema.extend({
    format: z.string().optional(),
    sorting: sortTypes.optional().default("asc"),
    color: z.string().optional().default("#0e58ff"),
    width: z.number().min(3).max(15).optional().default(5),
    num_categories: z.number().min(1).max(15).optional().default(1),
    show_other_aggregate: z.boolean().optional().default(false),
  })
});


export const pieChartConfigSchema = chartsConfigBaseSchema.extend({
  type: z.literal("pie_chart"),
  setup: chartConfigSetupBaseSchema.extend({
    field: z.string().optional(),
    operation: operationTypes.optional(),
    aggregation: z.string().optional(),
  }),
  options: chartConfigOptionsBaseSchema.extend({
    num_categories: z.number().min(1).max(15).optional().default(1),
    cap_others: z.boolean().optional().default(false),
  })
});

export type WidgetTypes = z.infer<typeof widgetTypes>;
export type OperationTypes = z.infer<typeof operationTypes>;
export type SortTypes = z.infer<typeof sortTypes>;
export type HistogramChartSchema = z.infer<typeof histogramChartConfigSchema>;
export type CategoriesChartSchema = z.infer<typeof categoriesChartConfigSchema>;
export type PieChartSchema = z.infer<typeof pieChartConfigSchema>;
export type WidgetChartConfig = HistogramChartSchema | CategoriesChartSchema | PieChartSchema;
