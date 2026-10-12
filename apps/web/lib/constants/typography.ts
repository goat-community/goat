/**
 * Shared typography constants for print-oriented report layouts.
 * The editor draws a family with the viewer's own font of that name. The print
 * worker has open fonts standing in for the ones it lacks, under their names
 * (apps/processes/workers/fonts/60-goat-print-fonts.conf), so a family added
 * here needs a font there too, or it prints in the generic fallback.
 */

export interface FontFamilyOption {
  label: string;
  value: string;
}

export const FONT_FAMILIES: FontFamilyOption[] = [
  // Sans-serif
  { label: "Arial", value: "Arial, sans-serif" },
  { label: "Helvetica", value: "Helvetica, Arial, sans-serif" },
  { label: "Verdana", value: "Verdana, Geneva, sans-serif" },
  { label: "Trebuchet MS", value: "'Trebuchet MS', sans-serif" },
  // Serif
  { label: "Times New Roman", value: "'Times New Roman', Times, serif" },
  { label: "Georgia", value: "Georgia, serif" },
  { label: "Garamond", value: "Garamond, serif" },
  // Monospace
  { label: "Courier New", value: "'Courier New', Courier, monospace" },
  { label: "Consolas", value: "Consolas, monospace" },
];

export interface FontSizeUnit {
  label: string;
  value: string;
}

export const FONT_SIZE_UNITS: FontSizeUnit[] = [
  { label: "pt", value: "pt" },
  { label: "mm", value: "mm" },
];

export const DEFAULT_FONT_SIZE = "12pt";
export const DEFAULT_FONT_FAMILY = "Arial, sans-serif";

/**
 * Default typography per legend text role.
 * These define the actual rendered defaults so the config panel stays in sync.
 */
export const LEGEND_TYPOGRAPHY_DEFAULTS: Record<string, TypographyStyle> = {
  title: { fontFamily: DEFAULT_FONT_FAMILY, fontSize: "11pt", fontWeight: "bold" },
  layerName: { fontFamily: DEFAULT_FONT_FAMILY, fontSize: "9pt", fontWeight: "bold" },
  legendItem: { fontFamily: DEFAULT_FONT_FAMILY, fontSize: "8pt", fontWeight: "normal" },
  caption: { fontFamily: DEFAULT_FONT_FAMILY, fontSize: "8pt", fontWeight: "normal" },
  heading: { fontFamily: DEFAULT_FONT_FAMILY, fontSize: "8pt", fontWeight: "normal", fontColor: "#666666" },
};

/**
 * Parse a CSS font-size string like "12pt" or "4mm" into value + unit.
 */
export function parseFontSize(value: string | null | undefined): { size: number; unit: string } {
  if (!value) return { size: 12, unit: "pt" };
  const match = value.match(/^(\d+(?:\.\d+)?)\s*(pt|mm)$/i);
  if (!match) return { size: 12, unit: "pt" };
  return { size: parseFloat(match[1]), unit: match[2].toLowerCase() };
}

/**
 * Format a numeric size + unit into a CSS font-size string.
 */
export function formatFontSize(size: number, unit: string): string {
  return `${size}${unit}`;
}

/**
 * Typography style interface used by report element configs (legend, etc.)
 */
export interface TypographyStyle {
  fontFamily?: string;
  fontSize?: string;
  fontColor?: string;
  fontWeight?: "normal" | "bold";
}
