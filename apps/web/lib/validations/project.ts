import * as z from "zod";

import { contentMetadataSchema, getContentQueryParamsSchema } from "@/lib/validations/common";
import { layerSchema } from "@/lib/validations/layer";
import { responseSchema } from "@/lib/validations/response";
import { publicUserSchema } from "@/lib/validations/user";

export const projectRoleEnum = z.enum(["project-owner", "project-viewer", "project-editor"]);

export const projectRoles = {
  OWNER: "project-owner",
  VIEWER: "project-viewer",
  EDITOR: "project-editor",
} as const;

export const projectShareRoleEnum = z.enum(["project-viewer", "project-editor"]);

export const shareProjectWithTeamOrOrganizationSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  avatar: z.string().optional(),
  role: projectShareRoleEnum,
})

export const shareProjectSchema = z.object({
  teams: z.array(shareProjectWithTeamOrOrganizationSchema).optional(),
  organizations: z.array(shareProjectWithTeamOrOrganizationSchema).optional(),
})


export const projectSchema = contentMetadataSchema.extend({
  folder_id: z.string(),
  id: z.string(),
  layer_order: z.array(z.number()),
  active_scenario_id: z.string().nullable(),
  updated_at: z.string(),
  created_at: z.string(),
  shared_with: shareProjectSchema.optional(),
  owned_by: publicUserSchema,
});

export const projectLayerSchema = layerSchema.extend({
  id: z.number(),
  folder_id: z.string(),
  query: z
    .object({
      metadata: z.object({}).optional(),
      cql: z.object({}).optional(),
    })
    .nullable()
    .optional(),
  layer_id: z.string().uuid(),
  charts: z.object({}).optional(),
  filtered_count: z.number().optional(),
  legend_urls: z.array(z.string()).optional(),
});

export const projectViewStateSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  zoom: z.number().min(0).max(24),
  min_zoom: z.number().min(0).max(24),
  max_zoom: z.number().min(0).max(24),
  bearing: z.number().min(0).max(360),
  pitch: z.number().min(0).max(60),
});

export const postProjectSchema = z.object({
  folder_id: z.string().optional(),
  name: z.string().optional(),
  description: z.string().optional(),
  tags: z.array(z.string()).optional(),
  thumbnail_url: z.string().optional(),
  layer_order: z.array(z.number()).optional(),
  active_scenario_id: z.string().optional(),
  initial_view_state: projectViewStateSchema.optional(),
});

const getProjectsQueryParamsSchema = getContentQueryParamsSchema.extend({});

export const projectResponseSchema = responseSchema(projectSchema);
export const projectLayersResponseSchema = responseSchema(projectLayerSchema);

export type Project = z.infer<typeof projectSchema>;
export type ProjectLayer = z.infer<typeof projectLayerSchema>;
export type ProjectPaginated = z.infer<typeof projectResponseSchema>;
export type PostProject = z.infer<typeof postProjectSchema>;
export type ProjectViewState = z.infer<typeof projectViewStateSchema>;
export type ProjectLayersPaginated = z.infer<typeof projectLayersResponseSchema>;
export type GetProjectsQueryParams = z.infer<typeof getProjectsQueryParamsSchema>;
export type ProjectSharedWith = z.infer<typeof shareProjectSchema>;
