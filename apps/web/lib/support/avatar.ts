import type { SupportTicketDetail } from "@/lib/validations/support";

const IMAGE_DATA_URI = /^data:image\/(?:jpeg|png|webp);base64,[A-Za-z0-9+/]+={0,2}$/;

/** A GOAT team member's photo from the ticket's `avatars`, or undefined (the avatar then shows initials).
 * Only image data URIs are accepted: anything else the response might carry is never used as an image source. */
export const supportAvatarSrc = (
  avatars: SupportTicketDetail["avatars"],
  contactId: number | null | undefined
): string | undefined => {
  if (contactId === null || contactId === undefined) return undefined;
  const value = avatars[String(contactId)];
  return value && IMAGE_DATA_URI.test(value) ? value : undefined;
};
