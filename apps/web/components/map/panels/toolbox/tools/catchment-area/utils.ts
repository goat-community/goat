import type { CatchmentAreaRoutingType } from "@/lib/validations/tools";
import { catchmentAreaConfigDefaults } from "@/lib/validations/tools";

import type { SelectorItem } from "@/types/map/common";

export const getTravelCostConfigValues = (min: number, max: number, ext?: string) => {
  const items = [] as SelectorItem[];
  for (let i = min; i <= max; i++) {
    items.push({
      value: i,
      label: `${i.toString()} ${ext ? ext : ""}`,
    });
  }
  return items;
};

export const getDefaultConfigValue = (
  routingType: CatchmentAreaRoutingType,
  configType: "speed" | "max_travel_time" | "max_distance" | "steps"
) => {
  const units: { [key: string]: string } = {
    speed: " km/h",
    max_travel_time: " min",
    max_distance: " m",
    steps: "",
  };

  const value = catchmentAreaConfigDefaults[routingType][configType];
  return {
    value,
    label: value + units[configType],
  };
};


export const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
};

