import { z } from "zod";

export const supportStatusSchema = z.enum(["new", "in_progress", "waiting", "solved", "cancelled"]);
export const supportCategorySchema = z.enum([
  "bug",
  "how_to",
  "data_issue",
  "feature_request",
  "account_billing",
  "other",
]);
export const supportImpactSchema = z.enum(["blocking", "slowing", "question"]);
export const supportRatingSchema = z.enum(["ko", "ok", "top"]);
export const supportViaSchema = z.enum(["app", "email"]);

export const supportTicketSchema = z.object({
  ref: z.string(),
  subject: z.string(),
  status: supportStatusSchema,
  category: supportCategorySchema,
  impact: supportImpactSchema.nullable(),
  customer_name: z.string().nullable(),
  customer_contact_id: z.number().nullable().default(null),
  is_mine: z.boolean(),
  agent_name: z.string().nullable(),
  via: supportViaSchema,
  created_at: z.string(),
  updated_at: z.string(),
  closed_at: z.string().nullable(),
  latest_message_author: z.string().nullable(),
  latest_message_is_agent: z.boolean(),
  latest_message_at: z.string().nullable(),
  unread: z.boolean(),
  needs_my_reply: z.boolean(),
});

export const supportAttachmentSchema = z.object({
  id: z.number(),
  name: z.string(),
  mimetype: z.string(),
  size: z.number(),
});

export const supportMessageSchema = z.object({
  id: z.number(),
  // only set for GOAT team members: the key into the detail's `avatars`
  author_contact_id: z.number().nullish(),
  author_name: z.string(),
  // false when the sender's contact was deleted: author_name is then ""
  author_known: z.boolean().default(true),
  is_agent: z.boolean(),
  is_me: z.boolean(),
  via: supportViaSchema,
  created_at: z.string(),
  body_html: z.string(),
  attachments: z.array(supportAttachmentSchema),
});

export const supportFollowerSchema = z.object({
  contact_id: z.number(),
  name: z.string(),
  is_me: z.boolean(),
});

export const supportTicketDetailSchema = z.object({
  ticket: supportTicketSchema,
  messages: z.array(supportMessageSchema),
  followers: z.array(supportFollowerSchema),
  on_ticket: z.boolean(),
  can_manage_people: z.boolean(),
  // GOAT team photos by contact id (as strings, JSON keys) as data URIs
  avatars: z.record(z.string(), z.string()).default({}),
  // The assigned agent's contact id (key into avatars), known before they have written
  agent_contact_id: z.number().nullable().default(null),
  // What the user already rated this solved ticket; null = not rated yet
  my_rating: supportRatingSchema.nullable().default(null),
});

export const supportSummarySchema = z.object({
  needs_reply: z.number(),
  unread: z.number(),
});
export const supportWriteResultSchema = z.object({
  ref: z.string(),
  message_id: z.number().nullable(),
  failed_files: z.array(z.string()),
});
export const supportColleagueSchema = z.object({
  user_id: z.string(),
  name: z.string(),
  email: z.string(),
  // matches a follower's contact_id; null until they get a contact
  contact_id: z.number().nullable().default(null),
});

export type SupportStatus = z.infer<typeof supportStatusSchema>;
export type SupportCategory = z.infer<typeof supportCategorySchema>;
export type SupportImpact = z.infer<typeof supportImpactSchema>;
export type SupportRating = z.infer<typeof supportRatingSchema>;
export type SupportTicket = z.infer<typeof supportTicketSchema>;
export type SupportAttachment = z.infer<typeof supportAttachmentSchema>;
export type SupportMessage = z.infer<typeof supportMessageSchema>;
export type SupportFollower = z.infer<typeof supportFollowerSchema>;
export type SupportTicketDetail = z.infer<typeof supportTicketDetailSchema>;
export type SupportSummary = z.infer<typeof supportSummarySchema>;
export type SupportWriteResult = z.infer<typeof supportWriteResultSchema>;
export type SupportColleague = z.infer<typeof supportColleagueSchema>;

export const SUPPORT_CATEGORIES: SupportCategory[] = supportCategorySchema.options;
export const SUPPORT_IMPACTS: SupportImpact[] = supportImpactSchema.options;
