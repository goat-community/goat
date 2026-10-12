import { ASSETS_URL } from "@/lib/constants";

export const PATTERN_IMAGES_BASE_URL = `${ASSETS_URL}/patterns`;

export type PatternImage = {
  name: string;
  url: string;
  width: number;
  height: number;
};

export const PATTERN_IMAGES: PatternImage[] = [
  {
    name: "stripe-diagonal-left",
    url: `${PATTERN_IMAGES_BASE_URL}/stripe-diagonal-left.svg`,
    width: 50,
    height: 50,
  },
  {
    name: "stripe-horizontal",
    url: `${PATTERN_IMAGES_BASE_URL}/stripe-horizontal.svg`,
    width: 50,
    height: 50,
  },
  {
    name: "grid",
    url: `${PATTERN_IMAGES_BASE_URL}/grid.svg`,
    width: 50,
    height: 50,
  }
]
