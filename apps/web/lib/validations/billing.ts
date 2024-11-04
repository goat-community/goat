import * as z from "zod";

const planSchema = z.object({
  plan_name: z.string(),
  title: z.string(),
  description: z.string(),
  highlights: z.array(z.string()).describe("List of key highlights and features of the plan"),
});

const plansListSchema = z.object({
  plans: z.array(planSchema),
});

export type Plan = z.infer<typeof planSchema>;
export type PlansList = z.infer<typeof plansListSchema>;
