import * as z from "zod";

const regionEnum = z.enum(["eu"]);

export const postOrganizationSchema = z.object({
  name: z.string().min(1).max(50),
  region: regionEnum,
});

export type PostOrganization = z.infer<typeof postOrganizationSchema>;
