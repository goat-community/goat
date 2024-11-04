/* eslint-disable @typescript-eslint/no-explicit-any */
import * as z from "zod";

export const responseSchema = <T extends z.ZodType<any, any, any>>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number(),
    page: z.number(),
    size: z.number(),
    pages: z.number(),
  });

export type Response<T extends z.ZodType<any, any, any>> = z.infer<ReturnType<typeof responseSchema<T>>>;
