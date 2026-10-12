// @vitest-environment node
import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

const ENTRYPOINT = path.resolve(__dirname, "../../entrypoint.sh");
const BUNDLE = 'x="APP_NEXT_PUBLIC_API_URL";y="APP_NEXT_PUBLIC_MAPBOX_TOKEN";z="APP_NEXT_PUBLIC_API_URL_V2"';

/** Applets the entrypoint calls, linked to busybox so a run sees the same
 * sed/tar/grep semantics as the node:alpine image. */
const BUSYBOX_APPLETS = ["sh", "sed", "tar", "grep", "env", "sort", "cut", "awk", "cat", "true", "echo"];
const BUSYBOX = ["/bin/busybox", "/usr/bin/busybox"].find((candidate) => existsSync(candidate));

type Shell = { name: string; command: string; path: string };

const shells = (): Shell[] => {
  const list: Shell[] = [{ name: "sh", command: "sh", path: "/usr/local/bin:/usr/bin:/bin" }];
  if (BUSYBOX) list.push({ name: "busybox sh", command: "sh", path: "" });
  return list;
};

describe.each(shells())("entrypoint.sh under $name", (shell) => {
  let webDir: string;
  let binDir: string;

  const bundle = () => readFileSync(path.join(webDir, ".next/static/a.js"), "utf8");

  const run = (env: Record<string, string>, args: string[] = ["true"]) =>
    execFileSync(shell.command, [ENTRYPOINT, ...args], {
      // A clean env: only what the test sets reaches the script.
      env: { NODE_ENV: "test", PATH: shell.path || binDir, WEB_DIR: webDir, ...env },
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    });

  const writeBundle = () => {
    mkdirSync(path.join(webDir, ".next/static"), { recursive: true });
    writeFileSync(path.join(webDir, ".next/static/a.js"), BUNDLE);
    writeFileSync(path.join(webDir, ".next/static/plain.js"), 'w="no placeholder"');
  };

  beforeEach(() => {
    webDir = mkdtempSync(path.join(tmpdir(), "goat-web-"));
    binDir = path.join(webDir, "bin");
    if (BUSYBOX) {
      mkdirSync(binDir);
      for (const applet of BUSYBOX_APPLETS) symlinkSync(BUSYBOX, path.join(binDir, applet));
    }
    writeBundle();
    execFileSync("tar", ["-cf", ".next-templates.tar", ".next/static/a.js"], { cwd: webDir });
  });

  afterEach(() => {
    rmSync(webDir, { recursive: true, force: true });
  });

  it("substitutes values carrying sed and shell metacharacters verbatim", () => {
    const value = "https://h.test/a?b=1&c=2#frag|x\\y z";
    run({ NEXT_PUBLIC_API_URL: value });
    expect(bundle()).toContain(`x="${value}";`);
  });

  it("re-applies from the pristine copy on every start", () => {
    run({ NEXT_PUBLIC_API_URL: "https://old.test" });
    run({ NEXT_PUBLIC_API_URL: "https://new.test" });
    expect(bundle()).toContain('x="https://new.test";');
    expect(bundle()).not.toContain("old.test");
  });

  it("leaves the placeholder of an unset variable", () => {
    run({ NEXT_PUBLIC_API_URL: "https://h.test" });
    expect(bundle()).toContain('y="APP_NEXT_PUBLIC_MAPBOX_TOKEN"');
  });

  it("replaces a name that extends another as a whole", () => {
    run({ NEXT_PUBLIC_API_URL: "https://one.test", NEXT_PUBLIC_API_URL_V2: "https://two.test" });
    expect(bundle()).toContain('x="https://one.test";');
    expect(bundle()).toContain('z="https://two.test"');
  });

  it("logs the names it sets, never the values", () => {
    const out = run({ NEXT_PUBLIC_API_URL: "https://h.test", NEXT_PUBLIC_MAPBOX_TOKEN: "pk.secret" });
    expect(out).toContain("NEXT_PUBLIC_MAPBOX_TOKEN");
    expect(out).not.toContain("pk.secret");
    expect(bundle()).toContain('y="pk.secret"');
  });

  it("substitutes in place when the image carries no pristine copy", () => {
    rmSync(path.join(webDir, ".next-templates.tar"));
    run({ NEXT_PUBLIC_API_URL: "https://h.test" });
    expect(bundle()).toContain('x="https://h.test";');
  });

  it("runs the given command", () => {
    const out = run({}, ["echo", "started"]);
    expect(out.trim().split("\n").pop()).toBe("started");
  });
});
