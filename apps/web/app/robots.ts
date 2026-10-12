import type { MetadataRoute } from "next";

import { DOCS_URL } from "@/lib/constants";
import { serverAppUrl } from "@/lib/utils/server-env";

// Read at request time: the app URL comes from the container environment.
export const dynamic = "force-dynamic";

/** Crawlers that collect content for AI assistants and search answers. */
const AI_CRAWLERS = [
  "GPTBot",
  "OAI-SearchBot",
  "ChatGPT-User",
  "ClaudeBot",
  "Claude-User",
  "Claude-SearchBot",
  "PerplexityBot",
  "Google-Extended",
  "Applebot-Extended",
  "CCBot",
];

const originOf = (url: string | undefined): string | undefined => {
  if (!url) return undefined;
  try {
    return new URL(url).origin;
  } catch {
    return undefined;
  }
};

const isNonProductionHost = (origin: string): boolean => {
  const host = new URL(origin).hostname;
  return host === "localhost" || /(^|[.-])(dev|staging)([.-]|$)/.test(host);
};

/**
 * Search engines and AI crawlers may read the documentation and public maps;
 * the signed-in app stays out of their indexes. Development and staging
 * hosts are closed entirely. The docs rules and sitemaps only apply when the
 * documentation is served from this host.
 */
export function buildRobots(appUrl: string | undefined, docsUrl: string): MetadataRoute.Robots {
  const appOrigin = originOf(appUrl);
  if (!appOrigin || isNonProductionHost(appOrigin)) {
    return { rules: [{ userAgent: "*", disallow: "/" }] };
  }

  const docs = new URL(docsUrl);
  const docsOnThisHost = docs.origin === appOrigin;
  const docsPath = docs.pathname.replace(/\/$/, "");

  const allow = ["/map/public/", "/_next/static/"];
  if (docsOnThisHost) allow.unshift(`${docsPath}/`);
  const rules = { allow, disallow: "/" };

  return {
    rules: [
      { userAgent: "*", ...rules },
      { userAgent: AI_CRAWLERS, ...rules },
    ],
    ...(docsOnThisHost && {
      sitemap: [`${appOrigin}${docsPath}/sitemap.xml`, `${appOrigin}${docsPath}/de/sitemap.xml`],
    }),
  };
}

export default function robots(): MetadataRoute.Robots {
  return buildRobots(serverAppUrl(), DOCS_URL);
}
