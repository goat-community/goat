// "Last updated" dates for the docs pages, from one `git log` pass.
//
// The Docker build has no .git, so CI writes the dates into last-updated.json
// before building the image (`node src/vcs/lastUpdated.js`). Builds from a
// checkout with full history read git directly; a shallow clone or no git at
// all leaves the dates out rather than showing wrong ones.

const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const SITE_DIR = path.resolve(__dirname, "../..");
const DATA_FILE = path.join(SITE_DIR, "last-updated.json");

function git(args) {
  return execFileSync("git", args, {
    cwd: SITE_DIR,
    encoding: "utf8",
    maxBuffer: 512 * 1024 * 1024,
    stdio: ["ignore", "pipe", "ignore"],
  });
}

/** Maps each Markdown file under the site dir (relative, "/"-separated) to the time of its last commit in ms. */
function readGitDates() {
  try {
    if (git(["rev-parse", "--is-shallow-repository"]).trim() !== "false") return null;
    // Newest commit first, so the first time a path shows up is its last change.
    const out = git(["log", "--relative", "--name-only", "--format=%x00%ct", "--", "."]);
    const dates = {};
    for (const commit of out.split("\0").slice(1)) {
      const [timestamp, ...files] = commit.split("\n");
      for (const file of files) {
        if (/\.mdx?$/.test(file) && !(file in dates)) dates[file] = Number(timestamp) * 1000;
      }
    }
    // Deleted files show up in the history too.
    for (const file of Object.keys(dates)) {
      if (!fs.existsSync(path.join(SITE_DIR, file))) delete dates[file];
    }
    return dates;
  } catch {
    return null;
  }
}

function readDataFile() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
  } catch {
    return {};
  }
}

/** A Docusaurus `future.experimental_vcs` config serving the dates above. */
function lastUpdatedVcs() {
  let dates;
  const load = () => {
    if (!dates) {
      const baked = readDataFile();
      dates = Object.keys(baked).length > 0 ? baked : (readGitDates() ?? {});
    }
    return dates;
  };
  const lookup = async (filePath) => {
    const key = path.relative(SITE_DIR, filePath).split(path.sep).join("/");
    const timestamp = load()[key];
    return timestamp ? { timestamp, author: "" } : null;
  };
  return {
    initialize: (_params) => {},
    getFileCreationInfo: async (_filePath) => null,
    getFileLastUpdateInfo: lookup,
  };
}

module.exports = { lastUpdatedVcs };

if (require.main === module) {
  const dates = readGitDates();
  if (!dates) {
    console.error("last-updated: needs a git checkout with full history (fetch-depth: 0)");
    process.exit(1);
  }
  fs.writeFileSync(DATA_FILE, `${JSON.stringify(dates)}\n`);
  console.log(`last-updated: ${Object.keys(dates).length} files -> ${path.relative(process.cwd(), DATA_FILE)}`);
}
