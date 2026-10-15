"use client";

import { Box, Link } from "@mui/material";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

const SAFE_PROTOCOLS = /^(https?:|mailto:)/i;

/** A link target the dock may render: http(s), mailto, or a path inside GOAT. */
export function safeHref(href: string | undefined): string | undefined {
  const value = href?.trim();
  if (!value) return undefined;
  // "//host" and "/\host" leave GOAT (browsers read a backslash as a slash).
  if (value.startsWith("/")) return /^\/[\\/]/.test(value) ? undefined : value;
  return SAFE_PROTOCOLS.test(value) ? value : undefined;
}

const COMPONENTS: Components = {
  a: ({ node: _, href, children }) => {
    const safe = safeHref(href);
    if (!safe) return <>{children}</>;
    return (
      <Link href={safe} target="_blank" rel="noopener noreferrer nofollow">
        {children}
      </Link>
    );
  },
  // A table wider than the dock scrolls on its own instead of widening the answer.
  table: ({ node: _, children }) => (
    <Box sx={{ overflowX: "auto", my: "8px" }}>
      <table>{children}</table>
    </Box>
  ),
};

const REMARK_PLUGINS = [remarkGfm];

const PROSE_SX = {
  fontSize: 13.5,
  lineHeight: 1.6,
  letterSpacing: "0.1px",
  color: "text.primary",
  overflowWrap: "anywhere",
  "& p": { my: "8px" },
  "& :first-of-type": { mt: 0 },
  "& :last-child": { mb: 0 },
  "& strong": { fontWeight: 700 },
  "& code": { fontFamily: "monospace", fontSize: 12.5 },
  "& pre": { whiteSpace: "pre-wrap", fontSize: 12 },
  "& ul, & ol": { pl: "20px", my: "8px" },
  "& li + li": { mt: "4px" },
  "& table": { borderCollapse: "collapse", fontSize: 12.5, lineHeight: 1.45 },
  "& th, & td": {
    px: "8px",
    py: "4px",
    borderBottom: 1,
    borderColor: "divider",
    textAlign: "left",
    verticalAlign: "top",
    overflowWrap: "normal",
  },
  "& th": { fontWeight: 700, whiteSpace: "nowrap" },
  "& th:first-of-type, & td:first-of-type": { pl: 0 },
} as const;

/**
 * An answer as safe Markdown (spec §10) with GitHub's extensions (tables,
 * strikethrough, bare links): no images (nothing loads by itself), no raw
 * HTML, and links only to safe targets, opened in a new tab. The URL transform
 * and the link component both apply `safeHref`, so a link that fails it
 * renders as its plain text.
 */
export default function SafeMarkdown({ children }: { children: string }) {
  return (
    <Box sx={PROSE_SX}>
      <ReactMarkdown
        remarkPlugins={REMARK_PLUGINS}
        skipHtml
        disallowedElements={["img"]}
        urlTransform={(url) => safeHref(url) ?? ""}
        components={COMPONENTS}>
        {children}
      </ReactMarkdown>
    </Box>
  );
}
