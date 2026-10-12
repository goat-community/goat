import { describe, expect, it } from "vitest";

import { EMPTY_DRAFT, sanitizeDraft, sanitizeFrom } from "../draft";

describe("sanitizeDraft", () => {
  it("keeps a valid draft", () => {
    const d = { category: "bug", subject: "s", description: "d", impact: "blocking", requestId: "abc" };
    expect(sanitizeDraft(d)).toEqual(d);
  });

  it("fills missing fields and drops unknown or mistyped values", () => {
    expect(sanitizeDraft({ category: "nope", impact: 3, subject: 7, description: null })).toEqual(
      EMPTY_DRAFT
    );
    expect(sanitizeDraft({ subject: "only" })).toEqual({ ...EMPTY_DRAFT, subject: "only" });
  });

  it("survives non-objects", () => {
    for (const raw of [null, undefined, "x", 4, ["bug"]]) expect(sanitizeDraft(raw)).toEqual(EMPTY_DRAFT);
  });
});

describe("sanitizeFrom", () => {
  const origin = "https://goat.example";
  it("keeps only the path of a same-origin value", () => {
    expect(sanitizeFrom("/map/1?x=1#h", origin)).toBe("/map/1");
    expect(sanitizeFrom("https://goat.example/a/b?q=1", origin)).toBe("/a/b");
  });
  it("ignores other origins, junk and empty values", () => {
    expect(sanitizeFrom("https://evil.example/x", origin)).toBe("");
    expect(sanitizeFrom("//evil.example/x", origin)).toBe("");
    expect(sanitizeFrom("javascript:alert(1)", origin)).toBe("");
    expect(sanitizeFrom(null, origin)).toBe("");
  });
  it("caps the length", () => {
    expect(sanitizeFrom(`/${"a".repeat(500)}`, origin)).toHaveLength(200);
  });
});
