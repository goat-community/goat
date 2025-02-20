import { Box, Typography, useTheme } from "@mui/material";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import useSWR from "swr";

import { HistogramChartSchema, PieChartSchema, WidgetChartConfig } from "@/lib/validations/widget";

// Color palette for charts
const COLORS = [
  "#0e58ff",
  "#f5b704",
  "#2a9d8f",
  "#ff6b6b",
  "#4ecdc4",
  "#45b7d1",
  "#96ceb4",
  "#ffeead",
  "#ff9999",
];

// Mock fetcher simulating API responses
const fetcher = async (url: string) => {
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate delay

  const mockData: Record<string, any> = {
    // Histogram data (pre-binned)
    "histogram-123": [
      { binStart: 0, binEnd: 10, count: 12 },
      { binStart: 10, binEnd: 20, count: 25 },
      { binStart: 20, binEnd: 30, count: 38 },
      { binStart: 30, binEnd: 40, count: 27 },
      { binStart: 40, binEnd: 50, count: 15 },
    ],

    // Pie chart data
    "pie-456": [
      { label: "Technology", value: 45 },
      { label: "Healthcare", value: 32 },
      { label: "Finance", value: 27 },
      { label: "Energy", value: 18 },
      { label: "Retail", value: 12 },
    ],
  };

  const id = url.split("/").pop();
  return mockData[id!] || null;
};

interface WidgetChartProps {
  config: WidgetChartConfig;
}

const WidgetChart: React.FC<WidgetChartProps> = ({ config }) => {
  const layerProjectId = config.setup?.layer_project_id;
  const data = {
    metadata: {
      dataset_id: "8721e2d9-58e0-4cbc-a431-94fb196819d3",
      aggregate_column: "lon",
      min_value: 6.9,
      max_value: 13.7,
      total_rows: 42,
      missing_values: 0,
    },
    bins: [
      { binStart: 6.9, binEnd: 7.6, count: 4 },
      { binStart: 7.6, binEnd: 8.3, count: 4 },
      { binStart: 8.3, binEnd: 9.0, count: 2 },
      { binStart: 9.0, binEnd: 9.7, count: 3 },
      { binStart: 9.7, binEnd: 10.3, count: 2 },
      { binStart: 10.3, binEnd: 11.0, count: 1 },
      { binStart: 11.0, binEnd: 11.7, count: 19 },
      { binStart: 11.7, binEnd: 12.4, count: 3 },
      { binStart: 12.4, binEnd: 13.1, count: 1 },
      { binStart: 13.1, binEnd: 13.7, count: 2 },
    ],
  };

  // if (!layerProjectId) return <div className="text-gray-500">No layer configured</div>;
  // if (error) return <div className="text-red-500">Error loading data</div>;
  // if (isLoading) return <div className="text-gray-500">Loading...</div>;
  if (!data) return null;

  return (
    <Box>
      <Typography variant="body1" fontWeight="bold" align="left" gutterBottom>
        {config.setup?.title}
      </Typography>

      {config.type === "histogram" ? (
        <HistogramChart config={config} data={data} />
      ) : (
        // <PieChartComponent config={config} data={data} />
        <></>
      )}
    </Box>
  );
};

// Histogram Component
interface HistogramResponse {
  metadata: {
    dataset_id: string;
    aggregate_column: string;
    min_value: number;
    max_value: number;
    total_rows: number;
    missing_values: number;
  };
  bins: Array<{
    binStart: number;
    binEnd: number;
    count: number;
  }>;
}

const HistogramChart = ({ config, data }: { config: HistogramChartSchema; data: HistogramResponse }) => {
  const { bins } = data;
  const theme = useTheme();
  return (
    <ResponsiveContainer width={"100%"} height={200}>
      <BarChart data={bins} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
        <XAxis
          dataKey="binStart"
          type="number" // Add type declaration
          domain={[data.metadata.min_value, data.metadata.max_value]} // Use actual min/max from metadata
          tickFormatter={(value) => `${value}`}
          label={{
            value: config.setup?.aggregation,
            position: "bottom",
            offset: 10,
          }}
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: theme.typography.caption.fontSize,
            fontFamily: theme.typography.fontFamily,
          }}
        />
        <Tooltip cursor={{ fill: "transparent" }} />
        <YAxis
          label={{ position: "left" }}
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: theme.typography.caption.fontSize,
            fontFamily: theme.typography.caption.fontFamily,
          }}
        />
        <Tooltip
          // labelFormatter={(binStart, payload) => {
          //   const bin = payload[0]?.payload;
          //   return `${bin.binStart} - ${bin.binEnd}`;
          // }}
          formatter={(value: number) => [value, "Count"]}
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
  );
};

// Pie Chart Component
const PieChartComponent = ({ config, data }: { config: PieChartSchema; data: any[] }) => {
  const { num_categories = 5, cap_others = true } = config.options || {};
  const sortedData = [...data].sort((a, b) => b.value - a.value);

  let displayData = sortedData;
  if (cap_others && num_categories < sortedData.length) {
    const othersValue = sortedData.slice(num_categories).reduce((sum, item) => sum + item.value, 0);

    displayData = [...sortedData.slice(0, num_categories), { label: "Others", value: othersValue }];
  }

  return (
    <PieChart>
      <Pie
        data={displayData}
        dataKey="value"
        nameKey="label"
        cx="50%"
        cy="50%"
        innerRadius={40}
        outerRadius={80}
        paddingAngle={2}
        label>
        {displayData.map((_, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="#fff" />
        ))}
      </Pie>
      <Tooltip
        formatter={(value: number, name: string) => [
          value,
          `${name} (${((value * 100) / displayData.reduce((a, b) => a + b.value, 0)).toFixed(1)}%)`,
        ]}
      />
    </PieChart>
  );
};

export default WidgetChart;
