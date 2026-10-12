import { describe, expect, it } from "vitest";

import { newTicketPath } from "../paths";

describe("newTicketPath", () => {
  it("carries the page the user came from", () => {
    expect(newTicketPath("/map/abc")).toBe("/support/new?from=%2Fmap%2Fabc");
  });

  it("names no page from the support pages themselves", () => {
    for (const from of [
      "/support",
      "/support/00040",
      "/support/new",
      "/support?tab=closed",
      null,
      undefined,
    ]) {
      expect(newTicketPath(from)).toBe("/support/new");
    }
    expect(newTicketPath("/supporters")).toBe("/support/new?from=%2Fsupporters");
  });
});
