import type { TFunction } from "i18next";
import { describe, expect, it, vi } from "vitest";

import { SupportRequestError } from "@/lib/api/support";

import { supportErrorMessage } from "../errors";

vi.mock("@/lib/api/support", () => ({
  SupportRequestError: class extends Error {
    constructor(
      public status: number,
      public detail: string
    ) {
      super(detail);
    }
  },
}));

const t = ((key: string) => key) as unknown as TFunction;

describe("supportErrorMessage", () => {
  it.each([
    [new SupportRequestError(429, ""), "support_rate_limited"],
    [new SupportRequestError(400, "too_many_files"), "support_too_many_files"],
    [new SupportRequestError(413, ""), "support_files_too_large"],
    [new SupportRequestError(400, "file_too_large"), "support_files_too_large"],
    [new SupportRequestError(403, "email_not_verified"), "support_email_not_verified"],
    [new SupportRequestError(422, "colleague_email_not_verified"), "support_colleague_email_not_verified"],
    [new SupportRequestError(422, "too_many_open_tickets"), "support_too_many_open_tickets"],
    [new SupportRequestError(422, "staff_email"), "support_staff_email"],
    [new SupportRequestError(422, "colleague_is_staff"), "support_colleague_is_staff"],
    [new SupportRequestError(401, ""), "support_unavailable"],
    [new SupportRequestError(403, "forbidden"), "support_unavailable"],
    [new SupportRequestError(404, ""), "support_unavailable"],
    [new SupportRequestError(422, "invalid_request"), "support_invalid"],
    [new SupportRequestError(400, ""), "support_invalid"],
    [new SupportRequestError(503, ""), "support_unavailable"],
    [new Error("network"), "support_unavailable"],
  ])("maps %s to %s", (error, message) => {
    expect(supportErrorMessage(t, error)).toBe(message);
  });

  it.each([
    [new SupportRequestError(403, "email_not_verified"), "support_email_not_verified"],
    [new SupportRequestError(403, "forbidden"), "support_forbidden"],
    [new SupportRequestError(404, ""), "support_not_found"],
    [new SupportRequestError(401, ""), "support_unavailable"],
    [new SupportRequestError(429, ""), "support_rate_limited"],
    [new SupportRequestError(413, ""), "support_files_too_large"],
    [new SupportRequestError(422, "invalid_request"), "support_invalid"],
    [new SupportRequestError(503, ""), "support_unavailable"],
    [new Error("network"), "support_unavailable"],
  ])("maps %s to %s for an action on an existing ticket", (error, message) => {
    expect(supportErrorMessage(t, error, { action: true })).toBe(message);
  });
});
