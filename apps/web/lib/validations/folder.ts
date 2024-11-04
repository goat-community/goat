import * as z from "zod";

export const folderSchema = z.object({
  name: z.string(),
  id: z.string().uuid(),
  user_id: z.string().uuid(),
});

export const folderResponse = z.array(folderSchema);

export type Folder = z.infer<typeof folderSchema>;
export type FolderResponse = z.infer<typeof folderResponse>;
