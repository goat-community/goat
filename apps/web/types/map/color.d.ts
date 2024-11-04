import type { MouseEvent } from "react";

import type { RGBColor } from "@/lib/constants/color";
import type { ColorMap, ColorRange } from "@/lib/validations/layer";
import type { ClassBreaks } from "@/lib/validations/layer";
import type { LayerFieldType } from "@/lib/validations/layer";

export type SingleColorSelectorProps = {
  onSelectColor: (color: RGBColor | ColorRange, e?: MouseEvent) => void;
  selectedColor: string;
};

export type ColorScaleSelectorProps = {
  selectedColorScaleMethod?: ClassBreaks;
  classBreaksValues?: LayerClassBreaks;
  setSelectedColorScaleMethod: (colorScale: ClassBreaks) => void;
  onCustomApply?: (colorMaps: ColorMap) => void;
  colorSet: ColorSet;
  label?: string;
  tooltip?: string;
  activeLayerId: string;
  activeLayerField: LayerFieldType;
  intervals: number;
};

// Key is HexColor but as key we can use only string
export type ColorLegends = { [key: string]: string };

export type ColorSet = {
  selectedColor: RGBColor | RGBAColor | ColorRange;
  setColor: (v: RGBColor | RGBAColor | ColorRange) => void;
  isRange?: boolean;
  label?: string;
};

export type RGBColor = [number, number, number];
export type RGBAColor = [number, number, number, number];
export type HexColor = string;

export type ColorItem = {
  id: string;
  color: string;
};

export type ValueItem = {
  id: string;
  values: string[] | null;
};

export type ColorMapItem = ColorItem & {
  value: string[] | null;
};
