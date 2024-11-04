import { invitationStatusEnum } from "@/lib/validations/invitation";
import * as z from "zod";

export const teamRoleEnum = z.enum([
  "team-owner",
  "team-member"
]);

export const teamRoles = {
  OWNER: "team-owner",
  MEMBER: "team-member"
} as const;


export const teamBaseSchema = z.object({
  name: z.string().min(1).max(50),
  description: z.string().min(1).max(250).optional(),
  avatar: z.string().optional().nullable()
});

export const teamSchema = teamBaseSchema.extend({
  id: z.string(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  role: teamRoleEnum
});

export const teamMemberSchema = z.object({
  id: z.string(),
  firstname: z.string().optional(),
  lastname: z.string().optional(),
  email: z.string().email(),
  role: teamRoleEnum,
  avatar: z.string().optional(),
  invitation_status: invitationStatusEnum.optional()
})

export const teamUpdateSchema = teamBaseSchema.partial()


export type TeamBase = z.infer<typeof teamBaseSchema>;
export type Team = z.infer<typeof teamSchema>;
export type TeamMember = z.infer<typeof teamMemberSchema>;
export type TeamUpdate = z.infer<typeof teamUpdateSchema>;
