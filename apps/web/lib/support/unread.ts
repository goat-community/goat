import type { SupportTicket } from "@/lib/validations/support";

/** Mirrors core: a closed ticket's replies still count as unread this long after its last activity. */
export const CLOSED_UNREAD_DAYS = 14;

/** Whether a closed ticket was closed (or last touched) within `CLOSED_UNREAD_DAYS`. */
export const isRecentlyClosed = (ticket: SupportTicket, now: number = Date.now()): boolean => {
  const stamps = [ticket.closed_at, ticket.updated_at]
    .filter((d): d is string => !!d)
    .map((d) => Date.parse(d))
    .filter((n) => !Number.isNaN(n));
  return stamps.length > 0 && Math.max(...stamps) >= now - CLOSED_UNREAD_DAYS * 86_400_000;
};
