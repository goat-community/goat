import type { SupportTicket } from "@/lib/validations/support";

/**
 * The agent to name as waiting for the user: the one who wrote the latest message, else none.
 * A stage set to "Waiting on Customer" without a message, or the assigned agent alone, asks
 * nothing the user can see, so callers fall back to the team.
 */
export const supportReplyAgent = (
  ticket: Pick<SupportTicket, "latest_message_is_agent" | "latest_message_author">
): string | null => (ticket.latest_message_is_agent ? (ticket.latest_message_author ?? null) : null);
