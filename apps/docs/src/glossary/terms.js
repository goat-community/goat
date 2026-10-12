// @ts-check

/**
 * Helpers for the Plan4Better website glossary, shared by the build plugin
 * (`src/plugins/glossary.js`) and the link preview (`GlossaryTerm`).
 * CommonJS so Node can require it and webpack can bundle it.
 */

const TERM_URL = /^https?:\/\/(?:www\.)?plan4better\.de\/(en\/glossary|de\/glossar)\/([a-z0-9-]+)\/?(?:[?#].*)?$/;
const JSON_LD = /<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;

/**
 * The lookup key of a glossary term link, e.g. "en/glossary/h3-grid", or null
 * when the address is not a single term on the website glossary.
 * @param {string | undefined} href
 * @returns {string | null}
 */
function termKey(href) {
  const match = typeof href === "string" ? TERM_URL.exec(href) : null;
  return match ? `${match[1]}/${match[2]}` : null;
}

/**
 * Every DefinedTerm in a glossary page's JSON-LD that has a name, a
 * description and a glossary term URL.
 * @param {string} html
 * @returns {{key: string, name: string, description: string, url: string}[]}
 */
function parseGlossaryTerms(html) {
  /** @type {{key: string, name: string, description: string, url: string}[]} */
  const terms = [];
  /** @param {any} node */
  const walk = (node) => {
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    if (!node || typeof node !== "object") {
      return;
    }
    if (node["@type"] === "DefinedTerm") {
      const key = termKey(node.url);
      if (key && typeof node.name === "string" && typeof node.description === "string") {
        terms.push({ key, name: node.name, description: node.description, url: node.url });
      }
    }
    Object.values(node).forEach(walk);
  };
  for (const [, block] of html.matchAll(JSON_LD)) {
    try {
      walk(JSON.parse(block));
    } catch {
      // A malformed block is skipped; the others may still hold the terms.
    }
  }
  return terms;
}

module.exports = { termKey, parseGlossaryTerms };
