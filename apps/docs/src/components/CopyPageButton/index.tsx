import Translate, { translate } from "@docusaurus/Translate";
import { useDoc } from "@docusaurus/plugin-content-docs/client";
import clsx from "clsx";
import React, { type ReactNode, useEffect, useRef, useState } from "react";

import styles from "./styles.module.css";

type Status = "idle" | "copied" | "failed";

const RESET_AFTER_MS = 2000;

/**
 * URL of a doc's Markdown source. `src/plugins/markdown-source.js` writes it
 * at build time next to the page: `<permalink>.md`, or `index.md` for a doc
 * served at a directory URL.
 */
export function markdownSourceUrl(permalink: string): string {
  return permalink.endsWith("/") ? `${permalink}index.md` : `${permalink}.md`;
}

async function fetchMarkdown(url: string): Promise<string> {
  const response = await fetch(url, { headers: { Accept: "text/markdown, text/plain" } });
  if (!response.ok) {
    throw new Error(`Fetching ${url} failed with ${response.status}`);
  }
  return response.text();
}

/** Copies through a hidden text field, for pages without the Clipboard API (plain http). */
function copyWithTextarea(text: string): void {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  if (!copied) {
    throw new Error("Copying to the clipboard was refused");
  }
}

/**
 * Safari only lets the clipboard be written during the click itself, so the
 * pending download is handed to a ClipboardItem there rather than awaited
 * first. Browsers without ClipboardItem get the text once it has arrived.
 */
async function copyMarkdown(url: string): Promise<void> {
  const text = fetchMarkdown(url);
  if (!navigator.clipboard) {
    copyWithTextarea(await text);
    return;
  }
  if (typeof ClipboardItem !== "undefined" && navigator.clipboard.write) {
    const blob = text.then((markdown) => new Blob([markdown], { type: "text/plain" }));
    await navigator.clipboard.write([new ClipboardItem({ "text/plain": blob })]);
    return;
  }
  await navigator.clipboard.writeText(await text);
}

function CopyIcon(): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" className={styles.icon}>
      <rect x="8" y="8" width="12" height="12" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M16 8V6.5A2.5 2.5 0 0 0 13.5 4h-7A2.5 2.5 0 0 0 4 6.5v7A2.5 2.5 0 0 0 6.5 16H8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function CheckIcon(): ReactNode {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" className={styles.icon}>
      <path
        d="m5 12.5 4.5 4.5L19 7.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Copies the current doc's Markdown source to the clipboard. */
export default function CopyPageButton({ className }: { className?: string }): ReactNode {
  const { metadata } = useDoc();
  const [status, setStatus] = useState<Status>("idle");
  const resetTimer = useRef<number | undefined>(undefined);

  useEffect(() => () => window.clearTimeout(resetTimer.current), []);

  const onClick = async () => {
    window.clearTimeout(resetTimer.current);
    try {
      await copyMarkdown(markdownSourceUrl(metadata.permalink));
      setStatus("copied");
    } catch {
      setStatus("failed");
    }
    resetTimer.current = window.setTimeout(() => setStatus("idle"), RESET_AFTER_MS);
  };

  return (
    <button
      type="button"
      className={clsx(styles.button, status === "copied" && styles.copied, className)}
      onClick={onClick}
      title={translate({
        id: "goat.copyPage.title",
        message: "Copy this page as Markdown",
        description: "Tooltip of the button that copies a doc page's Markdown source",
      })}>
      {status === "copied" ? <CheckIcon /> : <CopyIcon />}
      <span aria-live="polite">
        {status === "copied" ? (
          <Translate id="goat.copyPage.copied" description="Shown after a doc page's Markdown was copied">
            Copied
          </Translate>
        ) : status === "failed" ? (
          <Translate id="goat.copyPage.failed" description="Shown when copying a doc page's Markdown failed">
            Copy failed
          </Translate>
        ) : (
          <Translate
            id="goat.copyPage.label"
            description="Label of the button that copies a doc page's Markdown">
            Copy page
          </Translate>
        )}
      </span>
    </button>
  );
}
