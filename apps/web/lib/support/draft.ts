import {
  SUPPORT_CATEGORIES,
  SUPPORT_IMPACTS,
  type SupportCategory,
  type SupportImpact,
} from "@/lib/validations/support";

export type NewTicketDraft = {
  category: SupportCategory | null;
  subject: string;
  description: string;
  impact: SupportImpact | null;
  /** Idempotency key of the submit in flight (or last attempted); reused after a remount so the server dedupes. */
  requestId: string;
};

export const EMPTY_DRAFT: NewTicketDraft = {
  category: null,
  subject: "",
  description: "",
  impact: null,
  requestId: "",
};

const str = (v: unknown): string => (typeof v === "string" ? v : "");

/** A stored draft may be from an older version or hand-edited: keep only what the form can render. */
export const sanitizeDraft = (raw: unknown): NewTicketDraft => {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return EMPTY_DRAFT;
  const r = { ...EMPTY_DRAFT, ...(raw as Record<string, unknown>) };
  return {
    category: SUPPORT_CATEGORIES.includes(r.category as SupportCategory)
      ? (r.category as SupportCategory)
      : null,
    subject: str(r.subject),
    description: str(r.description),
    impact: SUPPORT_IMPACTS.includes(r.impact as SupportImpact) ? (r.impact as SupportImpact) : null,
    requestId: str(r.requestId),
  };
};

/** The page a ticket was opened from: same-origin path only, no query or hash, at most 200 characters. */
export const sanitizeFrom = (value: string | null, origin: string): string => {
  if (!value) return "";
  try {
    const url = new URL(value, origin);
    return url.origin === origin ? url.pathname.slice(0, 200) : "";
  } catch {
    return "";
  }
};
