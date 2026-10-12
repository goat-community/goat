// Run: node --test src/glossary/terms.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const { termKey, parseGlossaryTerms } = require("./terms");

test("termKey normalises English and German glossary term URLs", () => {
  assert.equal(termKey("https://www.plan4better.de/en/glossary/h3-grid"), "en/glossary/h3-grid");
  assert.equal(termKey("https://www.plan4better.de/de/glossar/h3-gitter"), "de/glossar/h3-gitter");
  assert.equal(termKey("https://plan4better.de/en/glossary/h3-grid/"), "en/glossary/h3-grid");
  assert.equal(termKey("https://www.plan4better.de/en/glossary/h3-grid#term"), "en/glossary/h3-grid");
});

test("termKey rejects anything that is not a single glossary term", () => {
  assert.equal(termKey("https://www.plan4better.de/en/glossary"), null);
  assert.equal(termKey("https://www.plan4better.de/en/contact/"), null);
  assert.equal(termKey("../data/builtin_datasets.md"), null);
  assert.equal(termKey(undefined), null);
});

test("parseGlossaryTerms reads DefinedTerm entries from JSON-LD", () => {
  const html = `<html><head>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","name":"x"}</script>
    <script type="application/ld+json">{"@context":"https://schema.org","@graph":[
      {"@type":"DefinedTermSet","hasDefinedTerm":[
        {"@type":"DefinedTerm","name":"H3 grid","description":"Hexagonal cells.","url":"https://www.plan4better.de/en/glossary/h3-grid"},
        {"@type":"DefinedTerm","name":"GTFS","description":"Timetables.","url":"https://www.plan4better.de/en/glossary/gtfs"}
      ]}]}</script>
  </head></html>`;
  assert.deepEqual(parseGlossaryTerms(html), [
    { key: "en/glossary/h3-grid", name: "H3 grid", description: "Hexagonal cells.", url: "https://www.plan4better.de/en/glossary/h3-grid" },
    { key: "en/glossary/gtfs", name: "GTFS", description: "Timetables.", url: "https://www.plan4better.de/en/glossary/gtfs" },
  ]);
});

test("parseGlossaryTerms skips broken JSON and incomplete terms", () => {
  const html = `<script type="application/ld+json">{not json</script>
    <script type="application/ld+json">[{"@type":"DefinedTerm","name":"No URL","description":"d"}]</script>`;
  assert.deepEqual(parseGlossaryTerms(html), []);
});

test("fetchGlossaryTerms returns no terms instead of throwing when a page is unreachable", async () => {
  const { fetchGlossaryTerms } = require("../plugins/glossary");
  const terms = await fetchGlossaryTerms(["http://127.0.0.1:9/glossary"]);
  assert.deepEqual(terms, {});
});
