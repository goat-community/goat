"use client";

import Script from "next/script";

/**
 * Injects the customer's Matomo tracker on a public dashboard.
 *
 * Defence-in-depth on the URL/site_id: the backend already validates
 * https-only, no query/fragment, and numeric site IDs. We re-validate here
 * at the trust boundary so a malformed or hostile JSONB row from the DB
 * can't end up in a <script> tag.
 *
 * Sends:
 *   - setDocumentTitle(projectName)        — readable in Matomo's UI
 *   - setCustomDimension(1, projectId)     — per-project breakdown
 *   - trackPageView + enableLinkTracking   — standard
 * We deliberately don't override `setCustomUrl`: each custom domain
 * shows up distinctly in Matomo, and the custom dimension gives the
 * dashboard-level grouping regardless of which URL the visitor used.
 */

interface Props {
  url: string;
  siteId: string;
  projectId: string;
  projectName?: string;
  /** When true, inject `_paq.push(['requireConsent'])` so the tracker
   * defers events until the visitor's consent banner calls
   * `_paq.push(['rememberConsentGiven'])`. When false there is no banner,
   * so the tracker runs cookieless (`disableCookies`): nothing is stored
   * on the device, which is what lets it count without consent (§25 TDDDG). */
  requireConsent?: boolean;
}

function isSafeMatomoUrl(u: string): boolean {
  try {
    const parsed = new URL(u);
    if (parsed.protocol !== "https:") return false;
    // A pathname is allowed — self-hosted Matomo often lives under one
    // (e.g. https://host.de/matomo/); the base is normalized to a trailing
    // slash before matomo.php/matomo.js are appended.
    return !parsed.search && !parsed.hash;
  } catch {
    return false;
  }
}

const SITE_ID_RE = /^\d+$/;

/** Matomo Cloud serves the JS from a separate CDN. Self-hosted serves it
 * from the same instance. Detect by hostname suffix. */
function matomoScriptSrc(base: string): string {
  try {
    const u = new URL(base);
    if (u.hostname.endsWith(".matomo.cloud")) {
      return `https://cdn.matomo.cloud/${u.hostname}/matomo.js`;
    }
  } catch {
    /* fall through */
  }
  return `${base}matomo.js`;
}

export function MatomoTracker({
  url,
  siteId,
  projectId,
  projectName,
  requireConsent = true,
}: Props) {
  if (!isSafeMatomoUrl(url) || !SITE_ID_RE.test(siteId)) {
    return null;
  }
  const base = url.endsWith("/") ? url : `${url}/`;
  const scriptSrc = matomoScriptSrc(base);
  // Stringify values so they're safe to embed in the script body.
  const baseJson = JSON.stringify(base);
  const siteJson = JSON.stringify(siteId);
  const projectIdJson = JSON.stringify(projectId);
  const titleJson = JSON.stringify(projectName ?? "");
  const scriptSrcJson = JSON.stringify(scriptSrc);
  // `requireConsent` / `disableCookies` MUST be pushed BEFORE `trackPageView`.
  // Otherwise the first pageview races the consent gate, or sets `_pk_id` /
  // `_pk_ses` before cookies are switched off. Done in code rather than
  // relying on the Matomo instance's "force tracking without cookies" setting,
  // so a dashboard without a banner can never set cookies.
  const consentLine = requireConsent ? "_paq.push(['requireConsent']);" : "_paq.push(['disableCookies']);";

  return (
    <Script id="matomo-tracker" strategy="afterInteractive">
      {`
        var _paq = window._paq = window._paq || [];
        ${consentLine}
        if (${titleJson}) { _paq.push(['setDocumentTitle', ${titleJson}]); }
        _paq.push(['setCustomDimension', 1, ${projectIdJson}]);
        _paq.push(['trackPageView']);
        _paq.push(['enableLinkTracking']);
        (function() {
          var u = ${baseJson};
          _paq.push(['setTrackerUrl', u+'matomo.php']);
          _paq.push(['setSiteId', ${siteJson}]);
          var d = document, g = d.createElement('script'), s = d.getElementsByTagName('script')[0];
          g.async = true; g.src = ${scriptSrcJson}; s.parentNode.insertBefore(g, s);
        })();
      `}
    </Script>
  );
}
