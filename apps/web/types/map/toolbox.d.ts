export interface IndicatorBaseProps {
  onBack: () => void;
  onClose: () => void;
}

export type ColumStatisticsOperation = "count" | "sum" | "mean" | "median" | "min" | "max";

export type areaSelectionTypes = "Polygon Layer" | "Hexagon bin";
