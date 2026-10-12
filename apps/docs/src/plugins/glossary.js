// @ts-check
const { parseGlossaryTerms } = require("../glossary/terms");

/** The website glossary pages whose terms get a preview in the docs. */
const GLOSSARY_PAGES = ["https://www.plan4better.de/en/glossary", "https://www.plan4better.de/de/glossar"];

/**
 * Glossary terms by key, read from the website. A page that cannot be read
 * is reported and skipped: its terms then render as plain links, and the
 * build carries on.
 * @param {string[]} urls
 * @returns {Promise<Record<string, {name: string, description: string, url: string}>>}
 */
async function fetchGlossaryTerms(urls) {
  /** @type {Record<string, {name: string, description: string, url: string}>} */
  const terms = {};
  await Promise.all(
    urls.map(async (url) => {
      try {
        const response = await fetch(url, { signal: AbortSignal.timeout(10000) });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const found = parseGlossaryTerms(await response.text());
        if (found.length === 0) {
          throw new Error("no glossary terms in the page");
        }
        for (const { key, ...term } of found) {
          terms[key] = term;
        }
      } catch (error) {
        // Node's fetch reports connection failures as "fetch failed"; the reason is in the cause.
        const cause = error instanceof Error ? /** @type {any} */ (error.cause) : undefined;
        const code = cause?.code ?? cause?.message;
        const reason = error instanceof Error ? error.message : String(error);
        console.warn(`[glossary] ${url}: ${reason}${typeof code === "string" ? ` (${code})` : ""}. Its links get no preview.`);
      }
    }),
  );
  return terms;
}

/**
 * Makes the website glossary available to `GlossaryTerm` as plugin data, so a
 * docs link to a glossary term can show the term's short description.
 * @returns {import('@docusaurus/types').Plugin<Record<string, {name: string, description: string, url: string}>>}
 */
function glossaryPlugin() {
  return {
    name: "glossary",
    loadContent() {
      return fetchGlossaryTerms(GLOSSARY_PAGES);
    },
    contentLoaded({ content, actions }) {
      actions.setGlobalData({ terms: content });
    },
  };
}

module.exports = glossaryPlugin;
module.exports.fetchGlossaryTerms = fetchGlossaryTerms;
