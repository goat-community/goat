import { describe, expect, it } from "vitest";

import { buildRobots } from "@/app/robots";

const DOCS = "https://goat.plan4better.de/docs";

const rulesFor = (robots: ReturnType<typeof buildRobots>, agent: string) =>
  (Array.isArray(robots.rules) ? robots.rules : [robots.rules]).find((r) =>
    Array.isArray(r.userAgent) ? r.userAgent.includes(agent) : r.userAgent === agent
  );

describe("robots.txt", () => {
  it("opens the docs and public maps on the host that serves the docs", () => {
    const robots = buildRobots("https://goat.plan4better.de", DOCS);
    expect(rulesFor(robots, "*")).toEqual({
      userAgent: "*",
      allow: ["/docs/", "/map/public/", "/_next/static/"],
      disallow: "/",
    });
    expect(robots.sitemap).toEqual([
      "https://goat.plan4better.de/docs/sitemap.xml",
      "https://goat.plan4better.de/docs/de/sitemap.xml",
    ]);
  });

  it("gives AI crawlers the same access as search engines", () => {
    const robots = buildRobots("https://goat.plan4better.de", DOCS);
    const ai = rulesFor(robots, "GPTBot");
    expect(ai?.allow).toContain("/docs/");
    expect(ai?.disallow).toBe("/");
    expect(rulesFor(robots, "ClaudeBot")).toBe(ai);
  });

  it("leaves docs rules out where the docs live elsewhere (self-hosted)", () => {
    const robots = buildRobots("https://goat.example.org", DOCS);
    expect(rulesFor(robots, "*")?.allow).toEqual(["/map/public/", "/_next/static/"]);
    expect(robots.sitemap).toBeUndefined();
  });

  it.each(["http://localhost:3000", "https://goat.dev.plan4better.de", "https://staging.goat.example.org"])(
    "closes %s completely",
    (url) => {
      expect(buildRobots(url, DOCS)).toEqual({ rules: [{ userAgent: "*", disallow: "/" }] });
    }
  );

  it("closes everything when the app URL is unknown", () => {
    expect(buildRobots(undefined, DOCS)).toEqual({ rules: [{ userAgent: "*", disallow: "/" }] });
  });
});
