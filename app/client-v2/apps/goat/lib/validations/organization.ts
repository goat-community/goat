import * as z from "zod";

export interface Organization {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  image_url: string;
  used_storage: number;
  total_storage: number;
  geocoding_quota: number;
  on_trial: boolean;
  region: string;
  contact_user_id: string;
  hubspot_id: string;
  suspended: boolean;
}

const regionEnum = z.enum(["eu"]);

export const postOrganizationSchema = z.object({
  name: z.string().min(1).max(50),
  region: regionEnum,
});

export type PostOrganization = z.infer<typeof postOrganizationSchema>;
