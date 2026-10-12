#!/usr/bin/env python3
"""Fail when a README or CLAUDE.md names a file or setting the code no longer has.

Docs rot silently: a renamed module or a removed setting leaves its mention
behind, and nothing notices until someone follows it. This checks the two
things that can be checked mechanically, in the files listed in DOCS:

- every path in backticks (`apps/core/src/...`, `config.py`, `deploy/compose/`)
  exists in the repository. A path with a slash is tried from the repo root,
  from the doc's directory and from the doc's `src/<package>` directory; a
  bare file name must exist somewhere under the doc's directory.
- in a service README, every setting name in backticks (`GOAT_PROCESSES_URL`,
  `DEFAULT_QUOTA_*`) occurs in that service's code or in goatlib.

Usage: scripts/check-doc-references.py   (from the repo root)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

# Docs to check. A README listed with a service directory also gets its
# setting names checked against that directory and goatlib.
DOCS: dict[str, str | None] = {
    "CLAUDE.md": None,
    "apps/docs/CLAUDE.md": None,
    "apps/web/CLAUDE.md": None,
    "apps/core/README.md": "apps/core",
    "apps/geoapi/README.md": "apps/geoapi",
    "apps/processes/README.md": "apps/processes",
    "apps/catalog/README.md": "apps/catalog",
    "packages/python/goatlib/README.md": "packages/python/goatlib",
}
SHARED_CODE = "packages/python/goatlib"

PATH_EXTENSIONS = {
    "py",
    "sql",
    "md",
    "yaml",
    "yml",
    "toml",
    "json",
    "sh",
    "ts",
    "tsx",
    "js",
    "mjs",
    "tpl",
}

# Named on purpose although the repository does not contain them: created
# only when needed (`check-file-sizes.sh` reads the exceptions list if present).
ALLOWED_MISSING = {".github/large-files.txt"}

CODE_SPAN = re.compile(r"`([^`\n]+)`")
SETTING = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?:_\*)?$")
# Prefixes a setting may be written with that the code spells without.
SETTING_PREFIXES = ("GEOAPI_", "CATALOG_")


def tracked_files() -> set[str]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return set(out.splitlines())


def candidate_paths(token: str, doc_dir: PurePosixPath) -> list[str]:
    base = token.rstrip("/")
    # A service's own modules are named relative to its package root.
    return [base, str(doc_dir / base), str(doc_dir / "src" / doc_dir.name / base)]


def looks_like_path(token: str) -> bool:
    """A repo path: a file with a known extension, or a directory written with
    an inner slash (`deploy/compose/`). Bare `name/` tokens are left alone,
    since docs use them for bucket prefixes too."""
    if any(ch in token for ch in " <>{}$*=…") or "..." in token or "://" in token:
        return False
    if token.startswith(("/", "f/", "-", "@")) or "your_" in token:
        return False  # URL routes, Windmill paths, CLI flags, npm scopes, placeholders
    has_ext = "." in token and token.rsplit(".", 1)[-1] in PATH_EXTENSIONS
    return has_ext or "/" in token.rstrip("/")


def is_gitignored(path: str) -> bool:
    """Local files such as `apps/core/.env` are mentioned in setup steps."""
    return subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0


def path_exists(
    token: str, doc_dir: PurePosixPath, files: set[str], dirs: set[str]
) -> bool:
    if token in ALLOWED_MISSING or ("/" in token and is_gitignored(token.rstrip("/"))):
        return True
    if "/" not in token.rstrip("/"):
        scope = "" if str(doc_dir) == "." else f"{doc_dir}/"
        name = token.rstrip("/")
        return any(
            f.startswith(scope)
            and (f.rsplit("/", 1)[-1] == name or f"/{name}/" in f"/{f}")
            for f in files
        )
    return any(c in files or c in dirs for c in candidate_paths(token, doc_dir))


def code_text(directories: list[str], files: set[str]) -> str:
    chunks = []
    for f in files:
        if f.startswith(tuple(f"{d}/" for d in directories)) and f.endswith(
            (".py", ".sql", ".toml", ".yaml", ".yml", ".sh")
        ):
            try:
                chunks.append((ROOT / f).read_text(errors="replace"))
            except OSError:
                continue
    return "\n".join(chunks).lower()


def setting_exists(token: str, code: str) -> bool:
    # Case-insensitive: pydantic settings may declare `enable_mcp` and read
    # it from `CATALOG_ENABLE_MCP` through an env prefix.
    name = (token[:-1] if token.endswith("_*") else token).lower()
    names = {name} | {
        name[len(p) :]
        for p in (x.lower() for x in SETTING_PREFIXES)
        if name.startswith(p)
    }
    return any(n in code for n in names)


def main() -> int:
    files = tracked_files()
    dirs = {
        str(PurePosixPath(f).parents[i])
        for f in files
        for i in range(len(PurePosixPath(f).parents) - 1)
    }
    problems: list[str] = []
    for doc, service in DOCS.items():
        doc_path = ROOT / doc
        if not doc_path.exists():
            problems.append(f"{doc}: listed in DOCS but missing")
            continue
        doc_dir = PurePosixPath(doc).parent
        code = code_text([service, SHARED_CODE], files) if service else ""
        for lineno, line in enumerate(doc_path.read_text().splitlines(), 1):
            for token in CODE_SPAN.findall(line):
                token = token.strip()
                if looks_like_path(token) and not path_exists(
                    token, doc_dir, files, dirs
                ):
                    problems.append(f"{doc}:{lineno}: path `{token}` does not exist")
                elif (
                    service and SETTING.match(token) and not setting_exists(token, code)
                ):
                    problems.append(
                        f"{doc}:{lineno}: setting `{token}` is not used in {service} or {SHARED_CODE}"
                    )
    for problem in problems:
        print(problem)
    if problems:
        print(
            f"\n{len(problems)} stale reference(s). Update the doc, or the code it describes."
        )
        return 1
    print(f"Checked {len(DOCS)} docs: every referenced path and setting exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
