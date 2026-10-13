import { describe, expect, it } from "vitest";

import { supportReplyAgent } from "../agent";

const ticket = (o: object) => ({
  latest_message_is_agent: true,
  latest_message_author: "Jonas",
  ...o,
});

describe("supportReplyAgent", () => {
  it("names the agent who wrote the latest message", () => {
    expect(supportReplyAgent(ticket({}))).toBe("Jonas");
  });

  it("names nobody when the latest message is not an agent's", () => {
    // e.g. the stage was set to "Waiting on Customer" without a message: the handler asked nothing
    expect(supportReplyAgent(ticket({ latest_message_is_agent: false }))).toBeNull();
    expect(supportReplyAgent(ticket({ latest_message_author: null }))).toBeNull();
  });
});
