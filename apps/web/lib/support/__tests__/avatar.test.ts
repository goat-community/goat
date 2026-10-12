import { describe, expect, it } from "vitest";

import { supportAvatarSrc } from "@/lib/support/avatar";
import { supportTicketDetailSchema } from "@/lib/validations/support";

const JPEG = "data:image/jpeg;base64,/9j/4AAQ";

describe("supportAvatarSrc", () => {
  it("returns the photo of the contact", () => {
    expect(supportAvatarSrc({ "26": JPEG }, 26)).toBe(JPEG);
    expect(supportAvatarSrc({ "26": "data:image/png;base64,iVBOR=" }, 26)).toContain("image/png");
    expect(supportAvatarSrc({ "26": "data:image/webp;base64,UklG" }, 26)).toContain("image/webp");
  });

  it("is undefined without a contact or a photo", () => {
    expect(supportAvatarSrc({ "26": JPEG }, null)).toBeUndefined();
    expect(supportAvatarSrc({ "26": JPEG }, undefined)).toBeUndefined();
    expect(supportAvatarSrc({ "26": JPEG }, 27)).toBeUndefined();
  });

  it("only accepts jpeg, png and webp data URIs", () => {
    for (const bad of [
      "data:image/svg+xml;base64,PHN2Zz4=",
      "data:text/html;base64,PGI+",
      "https://example.com/a.jpg",
      "javascript:alert(1)",
      'data:image/jpeg;base64,/9j/"onerror=alert(1)',
      "",
    ]) {
      expect(supportAvatarSrc({ "26": bad }, 26)).toBeUndefined();
    }
  });
});

describe("detail schema", () => {
  it("defaults avatars to an empty record", () => {
    expect(supportTicketDetailSchema.shape.avatars.parse(undefined)).toEqual({});
    expect(supportTicketDetailSchema.shape.avatars.parse({ "26": JPEG })).toEqual({ "26": JPEG });
  });

  it("defaults the agent contact and the rating to null", () => {
    expect(supportTicketDetailSchema.shape.agent_contact_id.parse(undefined)).toBeNull();
    expect(supportTicketDetailSchema.shape.agent_contact_id.parse(32)).toBe(32);
    expect(supportTicketDetailSchema.shape.my_rating.parse(undefined)).toBeNull();
    expect(supportTicketDetailSchema.shape.my_rating.parse("top")).toBe("top");
    expect(() => supportTicketDetailSchema.shape.my_rating.parse("great")).toThrow();
  });
});
