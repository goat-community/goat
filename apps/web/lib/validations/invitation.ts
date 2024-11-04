import * as z from "zod";

import { responseSchema } from "@/lib/validations/response";

export const invitationStatusEnum = z.enum(["pending", "canceled", "accepted", "rejected"]);
export const invitationTypeEnum = z.enum(["organization", "group"]);

export const invitationSchema = z.object({
  id: z.string().uuid(),
  send_by: z.string().uuid(),
  send_to: z.string().uuid().optional(),
  organization_id: z.string().uuid().optional(),
  team_id: z.string().uuid().optional(),
  type: invitationTypeEnum,
  payload: z.record(z.any()),
  expires: z.string().nullable(),
  status: invitationStatusEnum,
  created_at: z.string(),
  updated_at: z.string(),
});

export const inviationQueryParams = z.object({
  status: invitationStatusEnum.optional(),
  type: invitationTypeEnum.optional(),
  invitation_id: z.string().uuid().optional(),
  search: z.string().optional(),
});

export const invitationResponseSchema = responseSchema(invitationSchema);

export type Invitation = z.infer<typeof invitationSchema>;
export type InvitationPaginated = z.infer<typeof invitationResponseSchema>;
export type InvitationStatusType = z.infer<typeof invitationStatusEnum>;
export type InvitationType = z.infer<typeof invitationTypeEnum>;
