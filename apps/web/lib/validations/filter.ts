import * as z from "zod";

export enum FilterType {
  Logical = "logical",
  Spatial = "spatial",
}

export enum SpatialIntersectionGeomType {
  BBOX = "bbox",
  BOUNDARY = "boundary",
  DRAW = "draw",
}

export const filterTypeEnum = z.nativeEnum(FilterType);

export const expression = z.object({
  type: filterTypeEnum,
  attribute: z.string(),
  expression: z.string(),
  value: z.array(z.string().or(z.number())).or(z.string()).or(z.number()),
  id: z.string(),
  metadata: z
    .object({
      intersection: z
        .object({
          label: z.string().optional().default(""),
          geom_type: z.nativeEnum(SpatialIntersectionGeomType).optional(),
        })
        .optional(),
    })
    .optional(),
});

export type Expression = z.infer<typeof expression>;
