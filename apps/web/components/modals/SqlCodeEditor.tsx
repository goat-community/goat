"use client";

import type { ReactCodeMirrorRef } from "@uiw/react-codemirror";
import CodeMirror from "@uiw/react-codemirror";
import type { Completion, CompletionContext, CompletionResult, CompletionSource } from "@codemirror/autocomplete";
import { acceptCompletion, autocompletion, startCompletion } from "@codemirror/autocomplete";
import { sql, PostgreSQL } from "@codemirror/lang-sql";
import { Prec } from "@codemirror/state";
import { EditorView, keymap } from "@codemirror/view";
import { useTheme } from "@mui/material/styles";
import { useMemo } from "react";

// SQL keywords to auto-capitalize
const SQL_KEYWORDS = new Set([
  "select", "from", "where", "and", "or", "not", "in", "is", "null",
  "as", "on", "join", "left", "right", "inner", "outer", "cross",
  "full", "group", "by", "order", "having", "limit", "offset",
  "union", "all", "distinct", "insert", "into", "values", "update",
  "set", "delete", "create", "table", "drop", "alter", "index",
  "between", "like", "ilike", "exists", "case", "when", "then",
  "else", "end", "cast", "with", "recursive", "asc", "desc",
  "true", "false", "over", "partition", "rows", "range", "filter",
  "coalesce", "nullif", "using", "natural", "lateral", "fetch",
  "first", "next", "only", "except", "intersect",
]);

// Accept autocomplete and insert a trailing space
function acceptCompletionWithSpace(view: EditorView): boolean {
  if (acceptCompletion(view)) {
    const { head } = view.state.selection.main;
    view.dispatch(
      view.state.update({
        changes: { from: head, insert: " " },
        selection: { anchor: head + 1 },
      })
    );
    return true;
  }
  return false;
}

// Auto-capitalize SQL keywords after a separator is typed
const autoCapitalizeKeywords = EditorView.updateListener.of((update) => {
  if (!update.docChanged) return;

  let wordToCapitalize: { from: number; to: number; upper: string } | null = null;

  update.changes.iterChanges((_fromA, _toA, fromB, _toB, inserted) => {
    const text = inserted.toString();
    // Trigger on separator characters
    if (!/[\s,();.]/.test(text)) return;

    const pos = fromB;
    const doc = update.state.doc;
    const line = doc.lineAt(pos);
    const textBefore = line.text.slice(0, pos - line.from);
    const match = textBefore.match(/(\w+)$/);
    if (match) {
      const word = match[1];
      if (SQL_KEYWORDS.has(word.toLowerCase()) && word !== word.toUpperCase()) {
        wordToCapitalize = {
          from: pos - word.length,
          to: pos,
          upper: word.toUpperCase(),
        };
      }
    }
  });

  if (wordToCapitalize) {
    const { from, to, upper } = wordToCapitalize;
    setTimeout(() => {
      update.view.dispatch({
        changes: { from, to, insert: upper },
      });
    }, 0);
  }
});

/**
 * Force-open completion popup when the user types {{@.
 * CM6's activateOnTyping only fires for word characters, and @ is not one
 * in SQL context, so we need this manual trigger.
 */
function variableTrigger(variables: VariableInfo[]): ReturnType<typeof EditorView.updateListener.of> {
  return EditorView.updateListener.of((update) => {
    if (!update.docChanged || variables.length === 0) return;
    const pos = update.state.selection.main.head;
    const line = update.state.doc.lineAt(pos);
    const textBefore = line.text.slice(0, pos - line.from);
    if (/\{\{@[a-zA-Z_]?[a-zA-Z0-9_]*$/.test(textBefore)) {
      setTimeout(() => startCompletion(update.view), 0);
    }
  });
}

export interface VariableInfo {
  name: string;
  type: string;
  /** Display label; the completion shows it with the name to type beside it. */
  label?: string;
  /** Help text, shown in the completion's info panel. */
  description?: string;
}

/**
 * One {{@variable}} completion option. Matching runs on the name (what is
 * typed); the list shows the label, with the name next to it in the detail.
 */
export function variableCompletionOption(
  v: VariableInfo,
  closingBraces: number
): Completion {
  const label = v.label?.trim();
  const description = v.description?.trim();
  return {
    label: v.name,
    ...(label && label !== v.name && { displayLabel: label }),
    detail: label && label !== v.name ? `${v.name} · ${v.type}` : v.type,
    ...(description && { info: description }),
    type: "variable",
    apply: (view: EditorView, _completion: Completion, from: number, to: number) => {
      const insert = `${v.name}}}`;
      view.dispatch({
        changes: { from, to: to + closingBraces, insert },
        selection: { anchor: from + insert.length },
      });
    },
  };
}

/** CodeMirror completion source for {{@variable}} references */
function variableCompletionSource(variables: VariableInfo[]): CompletionSource {
  return (context: CompletionContext): CompletionResult | null => {
    const line = context.state.doc.lineAt(context.pos);
    const textBefore = line.text.slice(0, context.pos - line.from);
    const match = textBefore.match(/\{\{@([a-zA-Z_][a-zA-Z0-9_]*)?$/);
    if (!match) return null;

    const prefix = match[1] || "";
    const from = context.pos - prefix.length;

    // Check what follows the cursor — closeBrackets may have auto-inserted }}
    const textAfter = line.text.slice(context.pos - line.from);
    const closingBraces = textAfter.startsWith("}}") ? 2 : textAfter.startsWith("}") ? 1 : 0;

    return {
      from,
      options: variables.map((v) => variableCompletionOption(v, closingBraces)),
    };
  };
}

/**
 * Build a combined completion source that checks for {{@ variable patterns first,
 * then falls back to SQL language completions from language data.
 */
function combinedCompletionSource(variables: VariableInfo[]): CompletionSource {
  const varSource = variableCompletionSource(variables);

  return async (context: CompletionContext): Promise<CompletionResult | null> => {
    // Check for variable pattern first
    const varResult = varSource(context);
    if (varResult) return varResult;

    // Fall back to SQL language completions from language data
    const sources = context.state.languageDataAt<CompletionSource>("autocomplete", context.pos);
    for (const source of sources) {
      const result = await source(context);
      if (result) return result;
    }
    return null;
  };
}

interface SqlCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  schema: Record<string, string[]>;
  placeholder?: string;
  error?: boolean;
  editorRef?: React.MutableRefObject<ReactCodeMirrorRef | undefined>;
  variables?: VariableInfo[];
}

export default function SqlCodeEditor({
  value,
  onChange,
  schema,
  placeholder,
  error = false,
  editorRef,
  variables,
}: SqlCodeEditorProps) {
  const theme = useTheme();

  const sqlExtension = useMemo(
    () => sql({ dialect: PostgreSQL, schema, upperCaseKeywords: true }),
    [schema]
  );

  const editorTheme = useMemo(
    () =>
      EditorView.theme(
        {
          "&": {
            fontSize: "0.875rem",
            border: `1px solid ${error ? theme.palette.error.main : theme.palette.divider}`,
            borderRadius: "4px",
            backgroundColor: theme.palette.background.paper,
          },
          "&.cm-focused": {
            outline: "none",
            borderColor: error ? theme.palette.error.main : theme.palette.primary.main,
          },
          ".cm-content": {
            fontFamily: "monospace",
            padding: "8.5px 14px",
            caretColor: theme.palette.text.primary,
          },
          ".cm-gutters": {
            display: "none",
          },
          ".cm-placeholder": {
            color: theme.palette.text.disabled,
            fontFamily: "monospace",
          },
          ".cm-tooltip-autocomplete": {
            zIndex: "1400 !important",
          },
          ".cm-tooltip": {
            zIndex: "1400 !important",
          },
        },
        { dark: theme.palette.mode === "dark" }
      ),
    [error, theme]
  );

  // Tab accepts autocomplete + adds space (highest precedence)
  const tabKeymap = useMemo(
    () => Prec.highest(keymap.of([{ key: "Tab", run: acceptCompletionWithSpace }])),
    []
  );

  // When variables exist: single autocompletion extension with override that
  // handles both {{@ variable completions and SQL completions.
  // When no variables: no override, let basicSetup autocompletion handle SQL normally.
  const variableAutocompletion = useMemo(
    () => {
      if (!variables || variables.length === 0) return null;
      return autocompletion({
        override: [combinedCompletionSource(variables)],
        activateOnTyping: true,
      });
    },
    [variables]
  );

  const varTrigger = useMemo(
    () => (variables && variables.length > 0 ? variableTrigger(variables) : null),
    [variables]
  );

  const extensions = useMemo(
    () => [
      sqlExtension,
      tabKeymap,
      autoCapitalizeKeywords,
      editorTheme,
      ...(variableAutocompletion ? [variableAutocompletion] : []),
      ...(varTrigger ? [varTrigger] : []),
    ],
    [sqlExtension, tabKeymap, editorTheme, variableAutocompletion, varTrigger]
  );

  return (
    <CodeMirror
      ref={editorRef as React.Ref<ReactCodeMirrorRef>}
      value={value}
      onChange={onChange}
      extensions={extensions}
      placeholder={placeholder}
      theme={theme.palette.mode === "dark" ? "dark" : "light"}
      basicSetup={{
        lineNumbers: false,
        foldGutter: false,
        highlightActiveLine: false,
        bracketMatching: true,
        closeBrackets: true,
        autocompletion: !variableAutocompletion,
        history: true,
      }}
      minHeight="80px"
      maxHeight="200px"
    />
  );
}
