// @ts-check
const fs = require("fs/promises");
const path = require("path");

const FRONT_MATTER = /^---\r?\n[\s\S]*?\r?\n---\r?\n/;
const MDX_IMPORT = /^import\s.+\sfrom\s+["'][^"']+["'];?\s*$/;
const FENCE = /^\s*(```|~~~)/;
const HEADING_1 = /^#\s+\S/m;

/**
 * The Markdown a reader copies: the source without its front matter and
 * without the MDX import lines, which only matter to the site build. A doc
 * whose title comes from front matter gets it back as a heading.
 * @param {string} source
 * @param {string} title
 */
function readableMarkdown(source, title) {
  const body = source.replace(FRONT_MATTER, "");
  let inFence = false;
  const lines = body.split(/\r?\n/).filter((line) => {
    if (FENCE.test(line)) {
      inFence = !inFence;
      return true;
    }
    return inFence || !MDX_IMPORT.test(line);
  });
  const markdown = lines.join("\n").replace(/^\s*\n/, "");
  return HEADING_1.test(markdown) ? markdown : `# ${title}\n\n${markdown}`;
}

const LLMS_SUMMARY = {
  en:
    "GOAT is an open-source WebGIS platform for integrated planning, developed by Plan4Better. It brings together geospatial data management, interactive maps, accessibility analyses (catchment areas, heatmaps, travel time matrices), geoprocessing tools, reusable workflows, dashboards and print layouts. This documentation explains how to use GOAT in the browser, how its analysis tools and routing work, and how to host GOAT yourself.",
  de:
    "GOAT ist eine Open-Source-WebGIS-Plattform für die integrierte Planung, entwickelt von Plan4Better. Sie vereint Geodatenmanagement, interaktive Karten, Erreichbarkeitsanalysen (Einzugsgebiete, Heatmaps, Reisezeitmatrizen), Geoverarbeitungswerkzeuge, wiederverwendbare Workflows, Dashboards und Drucklayouts. Diese Dokumentation erklärt, wie Sie GOAT im Browser nutzen, wie die Analysewerkzeuge und das Routing funktionieren und wie Sie GOAT selbst betreiben.",
};

/** The sidebar section whose top-level categories each get their own `llms.txt` section. */
const SPLIT_SECTION = "section-user-manual";

/** Docs plugin instances and the sidebar each one contributes to `llms.txt`. */
const LLMS_SIDEBARS = [
  { pluginId: "default", sidebarId: "tutorialSidebar" },
  { pluginId: "tutorials", sidebarId: "tutorialsSidebar", label: "Tutorials" },
];

/**
 * URL path of a doc's Markdown copy. Mirrors `markdownSourceUrl` in
 * `src/components/CopyPageButton`.
 * @param {string} permalink
 */
function markdownUrlPath(permalink) {
  return permalink.endsWith("/") ? `${permalink}index.md` : `${permalink}.md`;
}

/** A description shorter than this ("Welcome!", "1.") takes in the next sentence too. */
const MIN_DESCRIPTION_LENGTH = 40;

/**
 * The first sentence of a description, as plain text on one line.
 * @param {string | undefined} text
 */
function firstSentence(text) {
  const plain = (text || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[*_`]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  const sentences = plain.match(/.+?(?:[.!?](?=\s|$)|$)/g) || [];
  let description = "";
  for (const sentence of sentences) {
    description = `${description} ${sentence.trim()}`.trim();
    if (description.length >= MIN_DESCRIPTION_LENGTH) {
      break;
    }
  }
  return description.replace(/:$/, "");
}

/**
 * The ids of the docs a sidebar item leads to, in sidebar order. Categories
 * marked `hidden` are left out, with everything beneath them.
 * @param {any} item
 * @returns {string[]}
 */
function sidebarDocIds(item) {
  if (item.type === "doc" || item.type === "ref") {
    return [item.id];
  }
  if (item.type !== "category" || (item.className || "").split(/\s+/).includes("hidden")) {
    return [];
  }
  const own = item.link && item.link.type === "doc" ? [item.link.id] : [];
  return [...own, ...item.items.flatMap(sidebarDocIds)];
}

/**
 * The `llms.txt` sections of a sidebar: one per sidebar section, except that
 * the categories of the user manual are listed one section each.
 * @param {any[]} sidebar
 * @param {string | undefined} label the section name of a sidebar that has no sections
 * @returns {{label: string, docIds: string[]}[]}
 */
function llmsSections(sidebar, label) {
  if (label) {
    return [{ label, docIds: sidebar.flatMap(sidebarDocIds) }];
  }
  return sidebar.flatMap((item) => {
    if (item.type === "category" && item.customProps?.section && item.key === SPLIT_SECTION) {
      return item.items.map((/** @type {any} */ child) => ({
        label: child.type === "category" ? `${item.label}: ${child.label}` : item.label,
        docIds: sidebarDocIds(child),
      }));
    }
    return [{ label: item.label || "", docIds: sidebarDocIds(item) }];
  });
}

/**
 * Writes the Markdown source of every doc (all docs plugin instances, in the
 * locale being built) next to its page as `<permalink>.md`. The "Copy page"
 * button fetches it from there. It also writes, at the root of the locale,
 * `llms.txt` (an index of those Markdown copies grouped like the sidebar,
 * following https://llmstxt.org) and `llms-full.txt` (the Markdown of every
 * page listed there, in the same order). None of it exists on the dev
 * server, which does not run `postBuild`.
 * @type {import('@docusaurus/types').PluginModule}
 */
module.exports = function markdownSourcePlugin(context) {
  return {
    name: "markdown-source",
    async postBuild({ plugins, outDir, siteDir, siteConfig, baseUrl }) {
      const origin = siteConfig.url.replace(/\/$/, "");
      const locale = context.i18n.currentLocale;
      const docsPlugins = plugins.filter((plugin) => plugin.name === "docusaurus-plugin-content-docs");
      /** @type {Map<string, Map<string, {doc: any, markdown: string}>>} */
      const pagesByPlugin = new Map();
      /** @type {{pluginId: string, sidebars: any}[]} */
      const sidebarsByPlugin = [];

      await Promise.all(
        docsPlugins.flatMap((plugin) => {
          /** @type {any} */
          const content = plugin.content;
          const pluginId = plugin.options.id ?? "default";
          const pages = new Map();
          pagesByPlugin.set(pluginId, pages);
          return (content?.loadedVersions ?? []).flatMap((/** @type {any} */ version) => {
            sidebarsByPlugin.push({ pluginId, sidebars: version.sidebars });
            return version.docs.map(async (/** @type {any} */ doc) => {
              const sourceFile = path.join(siteDir, doc.source.replace(/^@site\//, ""));
              const markdown = readableMarkdown(await fs.readFile(sourceFile, "utf8"), doc.title);
              pages.set(doc.id, { doc, markdown });
              const target = path.join(outDir, markdownUrlPath(doc.permalink).slice(baseUrl.length));
              await fs.mkdir(path.dirname(target), { recursive: true });
              await fs.writeFile(target, markdown);
            });
          });
        })
      );

      const index = [`# ${siteConfig.title}`, "", `> ${LLMS_SUMMARY[locale] ?? LLMS_SUMMARY.en}`];
      const full = [];
      for (const { pluginId, sidebarId, label } of LLMS_SIDEBARS) {
        const pages = pagesByPlugin.get(pluginId);
        const sidebar = sidebarsByPlugin.find((entry) => entry.pluginId === pluginId)?.sidebars?.[sidebarId];
        if (!pages || !sidebar) {
          continue;
        }
        for (const section of llmsSections(sidebar, label)) {
          const sectionPages = [...new Set(section.docIds)].map((id) => pages.get(id)).filter(Boolean);
          if (sectionPages.length === 0) {
            continue;
          }
          index.push("", `## ${section.label}`, "");
          for (const { doc, markdown } of sectionPages) {
            const description = firstSentence(doc.frontMatter.description || doc.description);
            const link = `- [${doc.title}](${origin}${markdownUrlPath(doc.permalink)})`;
            index.push(description && description !== doc.title ? `${link}: ${description}` : link);
            const body = markdown.replace(/^#\s+.*\r?\n+/, "");
            full.push(`# ${doc.title}\n\nSource: ${origin}${doc.permalink}\n\n${body.trim()}\n`);
          }
        }
      }
      await fs.writeFile(path.join(outDir, "llms.txt"), `${index.join("\n")}\n`);
      await fs.writeFile(path.join(outDir, "llms-full.txt"), full.join("\n"));
    },
  };
};
