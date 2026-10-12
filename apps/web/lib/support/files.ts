/** Per message sent (a new ticket or one reply) — mirrors core's support endpoint. */
export const SUPPORT_MAX_FILES = 10;
export const SUPPORT_MAX_FILE_BYTES = 10 * 1024 * 1024;
export const SUPPORT_MAX_TOTAL_BYTES = 50 * 1024 * 1024;

export type FileCheck =
  | { ok: true }
  | { ok: false; reason: "too_many_files" | "file_too_large" | "files_too_large"; name?: string };

export const checkFiles = (files: File[]): FileCheck => {
  if (files.length > SUPPORT_MAX_FILES) return { ok: false, reason: "too_many_files" };
  const tooLarge = files.find((f) => f.size > SUPPORT_MAX_FILE_BYTES);
  if (tooLarge) return { ok: false, reason: "file_too_large", name: tooLarge.name };
  const total = files.reduce((sum, f) => sum + f.size, 0);
  if (total > SUPPORT_MAX_TOTAL_BYTES) return { ok: false, reason: "files_too_large" };
  return { ok: true };
};
