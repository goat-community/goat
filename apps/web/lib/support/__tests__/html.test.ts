import { describe, expect, it } from "vitest";

import { prepareSupportHtml } from "@/lib/support/html";

describe("prepareSupportHtml", () => {
  it("drops scripts, images and event handlers but keeps text and links", () => {
    const { main } = prepareSupportHtml(
      '<p onclick="x()">Hi <a href="https://goat.example.org/docs">docs</a></p><script>alert(1)</script><img src="https://x/y.png">'
    );
    expect(main).toContain("Hi");
    expect(main).toContain('href="https://goat.example.org/docs"');
    expect(main).not.toContain("script");
    expect(main).not.toContain("<img");
    expect(main).not.toContain("onclick");
  });

  it("moves Odoo's quoted history and signatures into `quoted`", () => {
    const { main, quoted } = prepareSupportHtml(
      '<p>Answer</p><div data-o-mail-quote="1">-- <br>Anna Keller</div><blockquote data-o-mail-quote-container="1">old mail</blockquote>'
    );
    expect(main).toBe("<p>Answer</p>");
    expect(quoted).toContain("Anna Keller");
    expect(quoted).toContain("old mail");
  });

  it("strips every data-* attribute from the output", () => {
    const { main, quoted } = prepareSupportHtml(
      '<p data-foo="1" data-o-mail-quote-node="1">Hello <span data-x="y">there</span></p><div data-o-mail-quote="1" data-bar="2">sig</div>'
    );
    expect(main).not.toContain("data-");
    expect(quoted).not.toContain("data-");
    expect(main).toContain("Hello");
    expect(quoted).toContain("sig");
  });

  it("keeps http(s) and mailto links only, not relative or protocol-relative ones", () => {
    const { main } = prepareSupportHtml(
      '<a href="/settings">a</a><a href="//evil.example.com/x">b</a><a href="data:text/html,x">c</a><a href="https://ok.example.org">d</a>'
    );
    expect(main).not.toContain("/settings");
    expect(main).not.toContain("evil.example.com");
    expect(main).not.toContain("data:");
    expect(main).toContain('href="https://ok.example.org"');
  });

  it("drops javascript: hrefs", () => {
    const { main } = prepareSupportHtml('<a href="javascript:alert(1)">click</a>');
    expect(main).toContain("click");
    expect(main).not.toContain("javascript:");
  });

  it("adds target and rel to links in main and in quoted, and keeps mailto links", () => {
    const { main, quoted } = prepareSupportHtml(
      '<p><a href="https://goat.example.org">site</a> <a href="mailto:support@example.org">mail</a></p><div data-o-mail-quote="1"><a href="https://example.com/old">old</a></div>'
    );
    expect(main).toContain('href="mailto:support@example.org"');
    expect(main).toMatch(/<a [^>]*href="https:\/\/goat\.example\.org"[^>]*>/);
    for (const html of [main, quoted]) {
      expect(html).toContain('target="_blank"');
      expect(html).toContain('rel="noopener noreferrer"');
    }
    expect(quoted).toContain('href="https://example.com/old"');
  });
});
