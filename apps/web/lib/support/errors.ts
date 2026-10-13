import type { TFunction } from "i18next";

import { SupportRequestError } from "@/lib/api/support";
import { SUPPORT_EMAIL } from "@/lib/constants";

const FILE_LIMIT_DETAILS = ["file_too_large", "too_many_files", "files_too_large"];

/**
 * Maps a failed support request to a message: rate limit, file limits, bad input, or "unavailable" (5xx/network).
 * With `action`, the request acted on an existing ticket the user can see, so 403 means "not allowed to do
 * that" and 404 "ticket gone"; for the form they mean the feature is off or the session is invalid.
 */
export const supportErrorMessage = (
  t: TFunction,
  error: unknown,
  options: { action?: boolean } = {}
): string => {
  const status = error instanceof SupportRequestError ? error.status : 0;
  const detail = error instanceof SupportRequestError ? error.detail : "";
  if (status === 429) return t("support_rate_limited");
  // Core refuses to link a support contact to an unconfirmed email address (403, both create and reply).
  if (detail === "email_not_verified") return t("support_email_not_verified");
  // A colleague added to the ticket has not confirmed their email address (422).
  if (detail === "colleague_email_not_verified") return t("support_colleague_email_not_verified");
  if (detail === "too_many_open_tickets") return t("support_too_many_open_tickets");
  // The ticket system refuses contacts with a staff member's email (422): staff work in it directly.
  if (detail === "staff_email") return t("support_staff_email");
  if (detail === "colleague_is_staff") return t("support_colleague_is_staff");
  if (detail === "too_many_files") return t("support_too_many_files");
  // The server names no file, so "file_too_large" falls back to the generic size message.
  if (status === 413 || FILE_LIMIT_DETAILS.includes(detail)) return t("support_files_too_large");
  if (options.action && status === 403) return t("support_forbidden");
  if (options.action && status === 404) return t("support_not_found");
  // No valid session / not configured here: not something the user can fix by editing the form.
  if (status === 401 || status === 403 || status === 404)
    return t("support_unavailable", { email: SUPPORT_EMAIL });
  if (status >= 400 && status < 500) return t("support_invalid");
  return t("support_unavailable", { email: SUPPORT_EMAIL });
};
