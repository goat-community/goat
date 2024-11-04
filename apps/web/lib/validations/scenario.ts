import * as z from "zod";

import { responseSchema } from "@/lib/validations/response";

export const scenarioSchema = z.object({
  id: z.string(),
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  user_id: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const postScenarioSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
});

export const scenarioResponseSchema = responseSchema(scenarioSchema);

export const scenarioEditTypeEnum = z.enum(["n", "m", "d"]);

export const scenarioFeaturesPropertiesSchema = z
  .object({
    id: z.string(),
    layer_project_id: z.number(),
    feature_id: z.string(),
    edit_type: scenarioEditTypeEnum,
  })
  .catchall(z.unknown());

export const geometrySchema = z.object({
  type: z.string(),
  coordinates: z.array(z.unknown()),
});
export const scenarioFeatureSchema = z.object({
  type: z.string(),
  geometry: geometrySchema,
  id: z.string().nullable(),
  properties: scenarioFeaturesPropertiesSchema,
});


export const scenarioFeatures = z.object({
  type: z.string(),
  id: z.string(),
  features: z.array(scenarioFeatureSchema),
});

export const scenarioFeaturePost = z.object({
  id: z.string().optional(),
  feature_id: z.string().optional(),
  layer_project_id: z.number(),
  edit_type: z.string(),
  geom: z.string(),
  h3_3: z.number().optional(),
}).passthrough();

export const scenarioFeatureUpdate = scenarioFeaturePost.partial()

export type ScenarioEditType = z.infer<typeof scenarioEditTypeEnum>;
export type Scenario = z.infer<typeof scenarioSchema>;
export type ScenarioResponse = z.infer<typeof scenarioResponseSchema>;
export type ScenarioFeatures = z.infer<typeof scenarioFeatures>;
export type ScenarioFeature = z.infer<typeof scenarioFeatureSchema>;
export type PostScenario = z.infer<typeof postScenarioSchema>;

export type ScenarioFeaturePost = z.infer<typeof scenarioFeaturePost>;
export type ScenarioFeatureUpdate = z.infer<typeof scenarioFeatureUpdate>;
