import { Box, Divider, IconButton, Menu, MenuItem, Paper, Stack, Tooltip, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";
import type { SxProps, Theme } from "@mui/material";
import type { AnyExtension, Editor } from "@tiptap/core";
import { Color } from "@tiptap/extension-color";
import Link from "@tiptap/extension-link";
import TextAlign from "@tiptap/extension-text-align";
import { TextStyle } from "@tiptap/extension-text-style";
import Underline from "@tiptap/extension-underline";
import { EditorContent, useEditor, useEditorState } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import type { ReactNode } from "react";
import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import FontSize from "@/lib/extensions/font-size";

import { rgbToHex } from "@/lib/utils/helpers";

import type { RGBColor } from "@/types/map/color";

import { ArrowPopper } from "@/components/ArrowPoper";
import SingleColorSelector from "@/components/map/panels/style/color/SingleColorSelector";
import LinkPopover from "@/components/builder/widgets/data/LinkPopover";

/**
 * Base extensions every InlineRichTextEditor toolbar depends on. Export
 * so callers passing a custom `extensions` list can include them:
 *
 *   extensions={[...DEFAULT_INLINE_EXTENSIONS, MyCustomExtension]}
 *
 * If you pass `extensions` WITHOUT these, the corresponding toolbar
 * buttons (color, font size, link, alignment) will throw at runtime
 * because TipTap's chainable commands aren't registered.
 */
export const DEFAULT_INLINE_EXTENSIONS: AnyExtension[] = [
  // StarterKit (TipTap 3) bundles Underline and a basic Link extension.
  // Disable both so we can register our own — Link needs custom config
  // (openOnClick:false, target=_blank) — without TipTap warning about
  // duplicate extension names.
  StarterKit.configure({ underline: false, link: false }),
  Underline,
  TextAlign.configure({ types: ["heading", "paragraph"] }),
  TextStyle,
  FontSize,
  Color,
  Link.configure({
    openOnClick: false,
    HTMLAttributes: { target: "_blank", rel: "noopener noreferrer" },
  }),
];

const HEADING_LEVELS: Array<{ value: 0 | 1 | 2 | 3; labelKey: string }> = [
  { value: 0, labelKey: "body_text" },
  { value: 1, labelKey: "heading_1" },
  { value: 2, labelKey: "heading_2" },
  { value: 3, labelKey: "heading_3" },
];

const FONT_SIZE_PRESETS = [10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48];

const ALIGN_OPTIONS: Array<{
  value: "left" | "center" | "right" | "justify";
  icon: ICON_NAME;
  labelKey: string;
}> = [
  { value: "left", icon: ICON_NAME.ALIGN_LEFT, labelKey: "align_left" },
  { value: "center", icon: ICON_NAME.ALIGN_CENTER, labelKey: "align_center" },
  { value: "right", icon: ICON_NAME.ALIGN_RIGHT, labelKey: "align_right" },
  { value: "justify", icon: ICON_NAME.ALIGN_JUSTIFY, labelKey: "justify" },
];

interface ToolbarState {
  isBold: boolean;
  isItalic: boolean;
  isUnderline: boolean;
  isStrike: boolean;
  isBulletList: boolean;
  isOrderedList: boolean;
  isLink: boolean;
  headingLevel: number;
  fontSize: number;
  alignment: "left" | "center" | "right" | "justify";
  color: string | null;
}

function parsePxSize(value: string | null | undefined): number {
  if (!value) return 16;
  const match = value.match(/^(\d+(?:\.\d+)?)\s*px$/i);
  return match ? parseFloat(match[1]) : 16;
}

function selectToolbarState({ editor }: { editor: Editor | null }): ToolbarState | null {
  if (!editor) return null;
  const level = ([1, 2, 3, 4, 5, 6] as const).find((l) =>
    editor.isActive("heading", { level: l }),
  );
  const fontSize = editor.getAttributes("textStyle").fontSize as string | undefined;
  const color = (editor.getAttributes("textStyle").color as string | undefined) ?? null;
  const alignment = (["center", "right", "justify"] as const).find((a) =>
    editor.isActive({ textAlign: a }),
  ) ?? "left";
  return {
    isBold: editor.isActive("bold"),
    isItalic: editor.isActive("italic"),
    isUnderline: editor.isActive("underline"),
    isStrike: editor.isActive("strike"),
    isBulletList: editor.isActive("bulletList"),
    isOrderedList: editor.isActive("orderedList"),
    isLink: editor.isActive("link"),
    headingLevel: level ?? 0,
    fontSize: parsePxSize(fontSize),
    alignment,
    color,
  };
}

// Dense toolbar toggle. Used for B/I/U/S, lists, link, clear.
function ToolbarBtn({
  active,
  onClick,
  icon,
  tooltip,
  children,
}: {
  active?: boolean;
  onClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
  icon?: ICON_NAME;
  tooltip?: string;
  children?: ReactNode;
}) {
  const btn = (
    <IconButton
      size="small"
      disableRipple
      onClick={onClick}
      sx={(theme) => ({
        width: 26,
        height: 26,
        p: 0,
        borderRadius: 0.75,
        color: active ? "primary.main" : "text.secondary",
        bgcolor: active ? alpha(theme.palette.primary.main, 0.12) : "transparent",
        "&:hover": {
          bgcolor: active
            ? alpha(theme.palette.primary.main, 0.18)
            : theme.palette.action.hover,
          color: active ? "primary.main" : "text.primary",
        },
      })}>
      {icon ? <Icon iconName={icon} style={{ fontSize: 14 }} htmlColor="inherit" /> : children}
    </IconButton>
  );
  return tooltip ? <Tooltip title={tooltip}>{btn}</Tooltip> : btn;
}

// Dropdown trigger — same visual weight as ToolbarBtn but renders a text
// or icon label plus a chevron. Uses a ref for the anchor element so the
// Menu's position is always derived from the live DOM, not from state
// that could go stale across re-renders triggered by useEditorState.
function ToolbarDropdown({
  label,
  icon,
  active,
  width,
  children,
}: {
  label?: string;
  icon?: ICON_NAME;
  active?: boolean;
  width?: number;
  children: (close: () => void) => ReactNode;
}) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  const closeMenu = () => setOpen(false);

  return (
    <>
      <IconButton
        ref={buttonRef}
        size="small"
        disableRipple
        onClick={() => setOpen(true)}
        sx={(theme) => ({
          height: 26,
          minWidth: width,
          px: 0.5,
          borderRadius: 0.75,
          gap: 0.25,
          color: open || active ? "primary.main" : "text.secondary",
          bgcolor:
            open || active ? alpha(theme.palette.primary.main, 0.12) : "transparent",
          "&:hover": {
            bgcolor:
              open || active
                ? alpha(theme.palette.primary.main, 0.18)
                : theme.palette.action.hover,
            color: open || active ? "primary.main" : "text.primary",
          },
        })}>
        {icon && <Icon iconName={icon} style={{ fontSize: 14 }} htmlColor="inherit" />}
        {label && (
          <Typography
            variant="caption"
            sx={{ fontSize: 11, fontWeight: 600, lineHeight: 1, color: "inherit" }}>
            {label}
          </Typography>
        )}
        <Icon iconName={ICON_NAME.CHEVRON_DOWN} style={{ fontSize: 10 }} htmlColor="inherit" />
      </IconButton>
      <Menu
        anchorEl={buttonRef.current}
        open={open}
        onClose={closeMenu}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
        transformOrigin={{ vertical: "top", horizontal: "left" }}
        slotProps={{ paper: { sx: { mt: 0.5, minWidth: 120 } } }}>
        {children(closeMenu)}
      </Menu>
    </>
  );
}

export interface InlineRichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  extensions?: AnyExtension[];
  toolbarExtras?: (editor: Editor) => ReactNode;
  minHeight?: number;
  contentSx?: SxProps<Theme>;
}

export function InlineRichTextEditor({
  value,
  onChange,
  extensions,
  toolbarExtras,
  minHeight = 96,
  contentSx,
}: InlineRichTextEditorProps) {
  const { t } = useTranslation("common");
  const editor = useEditor({
    immediatelyRender: false,
    extensions: extensions ?? DEFAULT_INLINE_EXTENSIONS,
    content: value,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
  });
  const state = useEditorState({ editor, selector: selectToolbarState });

  // Link trigger uses a ref-based anchor (its own popover keeps stable
  // anchorEl across re-renders). The color picker uses ArrowPopper with
  // callback-ref anchoring, so no ref needed here for it.
  const linkRef = useRef<HTMLButtonElement>(null);
  const [colorOpen, setColorOpen] = useState(false);
  const [linkOpen, setLinkOpen] = useState(false);

  if (!editor || !state) return null;

  const sep = (
    <Divider
      orientation="vertical"
      flexItem
      sx={(theme) => ({
        my: 0.5,
        mx: 0.25,
        borderColor: alpha(theme.palette.text.primary, 0.08),
      })}
    />
  );

  const handleColor = (rgb: RGBColor) => {
    const hex = rgbToHex(rgb);
    editor.chain().focus().setColor(hex).run();
  };

  const headingLabel =
    state.headingLevel === 0 ? t("body_text") : `H${state.headingLevel}`;
  const currentColorHex = state.color ?? "#000000";

  return (
    <Box>
      {/* Toolbar */}
      <Stack
        direction="row"
        spacing={0.25}
        alignItems="center"
        sx={(theme) => ({
          p: 0.5,
          flexWrap: "wrap",
          rowGap: 0.25,
          border: 1,
          borderColor: alpha(theme.palette.text.primary, 0.1),
          borderBottom: 0,
          borderTopLeftRadius: 6,
          borderTopRightRadius: 6,
        })}>
        <ToolbarDropdown label={headingLabel} width={56}>
          {(close) =>
            HEADING_LEVELS.map((h) => (
              <MenuItem
                key={h.value}
                dense
                selected={state.headingLevel === h.value}
                onClick={() => {
                  if (h.value === 0) {
                    editor.chain().focus().setParagraph().run();
                  } else {
                    editor.chain().focus().toggleHeading({ level: h.value }).run();
                  }
                  close();
                }}
                sx={{ fontSize: 13 }}>
                {t(h.labelKey)}
              </MenuItem>
            ))
          }
        </ToolbarDropdown>
        <ToolbarDropdown label={`${state.fontSize}`} width={44}>
          {(close) =>
            FONT_SIZE_PRESETS.map((size) => (
              <MenuItem
                key={size}
                dense
                selected={state.fontSize === size}
                onClick={() => {
                  editor.chain().focus().setFontSize(`${size}px`).run();
                  close();
                }}
                sx={{ fontSize: 13 }}>
                {size}px
              </MenuItem>
            ))
          }
        </ToolbarDropdown>
        {sep}
        <ToolbarBtn
          active={state.isBold}
          onClick={() => editor.chain().focus().toggleBold().run()}
          icon={ICON_NAME.BOLD}
        />
        <ToolbarBtn
          active={state.isItalic}
          onClick={() => editor.chain().focus().toggleItalic().run()}
          icon={ICON_NAME.ITALIC}
        />
        <ToolbarBtn
          active={state.isUnderline}
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          icon={ICON_NAME.UNDERLINE}
        />
        <ToolbarBtn
          active={state.isStrike}
          onClick={() => editor.chain().focus().toggleStrike().run()}
          icon={ICON_NAME.STRIKETHROUGH}
        />
        <ArrowPopper
          open={colorOpen}
          placement="bottom"
          arrow={false}
          disablePortal={false}
          isClickAwayEnabled={true}
          onClose={() => setColorOpen(false)}
          content={
            <Paper
              sx={{
                py: 2,
                boxShadow: "rgba(0, 0, 0, 0.16) 0px 6px 12px 0px",
                width: 235,
                maxHeight: 500,
              }}>
              <SingleColorSelector
                selectedColor={currentColorHex}
                onSelectColor={(c) => {
                  if (Array.isArray(c) && c.length === 3) {
                    handleColor(c as RGBColor);
                  }
                }}
              />
            </Paper>
          }>
          <IconButton
            size="small"
            disableRipple
            onClick={() => setColorOpen((v) => !v)}
            sx={(theme) => ({
              width: 26,
              height: 26,
              p: 0,
              borderRadius: 0.75,
              color: colorOpen ? "primary.main" : "text.secondary",
              bgcolor: colorOpen ? alpha(theme.palette.primary.main, 0.12) : "transparent",
              "&:hover": {
                bgcolor: colorOpen
                  ? alpha(theme.palette.primary.main, 0.18)
                  : theme.palette.action.hover,
                color: colorOpen ? "primary.main" : "text.primary",
              },
            })}>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                lineHeight: 1,
              }}>
              <Typography component="span" sx={{ fontSize: 11, fontWeight: 700, lineHeight: 1 }}>
                A
              </Typography>
              <Box
                sx={{
                  width: 14,
                  height: 3,
                  borderRadius: 0.5,
                  bgcolor: currentColorHex,
                  mt: "1px",
                }}
              />
            </Box>
          </IconButton>
        </ArrowPopper>
        {sep}
        <ToolbarBtn
          active={state.isBulletList}
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          icon={ICON_NAME.BULLET_LIST}
        />
        <ToolbarBtn
          active={state.isOrderedList}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          icon={ICON_NAME.NUMBERED_LIST}
        />
        {sep}
        {/* Align dropdown — current alignment shown as the icon. */}
        <ToolbarDropdown
          icon={
            ALIGN_OPTIONS.find((a) => a.value === state.alignment)?.icon ??
            ICON_NAME.ALIGN_LEFT
          }>
          {(close) =>
            ALIGN_OPTIONS.map((a) => (
              <MenuItem
                key={a.value}
                dense
                selected={state.alignment === a.value}
                onClick={() => {
                  editor.chain().focus().setTextAlign(a.value).run();
                  close();
                }}>
                <Icon iconName={a.icon} style={{ fontSize: 14, marginRight: 8 }} />
                <Typography variant="caption" sx={{ fontSize: 13 }}>
                  {t(a.labelKey)}
                </Typography>
              </MenuItem>
            ))
          }
        </ToolbarDropdown>
        {sep}
        <Tooltip title={state.isLink ? t("edit_link") : t("add_link")}>
          <IconButton
            ref={linkRef}
            size="small"
            disableRipple
            onClick={() => setLinkOpen(true)}
            sx={(theme) => {
              const isActive = state.isLink || linkOpen;
              return {
                width: 26,
                height: 26,
                p: 0,
                borderRadius: 0.75,
                color: isActive ? "primary.main" : "text.secondary",
                bgcolor: isActive ? alpha(theme.palette.primary.main, 0.12) : "transparent",
                "&:hover": {
                  bgcolor: isActive
                    ? alpha(theme.palette.primary.main, 0.18)
                    : theme.palette.action.hover,
                  color: isActive ? "primary.main" : "text.primary",
                },
              };
            }}>
            <Icon iconName={ICON_NAME.LINK} style={{ fontSize: 14 }} htmlColor="inherit" />
          </IconButton>
        </Tooltip>
        <ToolbarBtn
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
          tooltip={t("clear_formatting")}>
          <Typography
            component="span"
            sx={{
              fontSize: 12,
              fontWeight: 700,
              lineHeight: 1,
              textDecoration: "line-through",
              color: "inherit",
            }}>
            T
          </Typography>
        </ToolbarBtn>
        {toolbarExtras && (
          <>
            {sep}
            <Box sx={{ pl: 0.75, display: "inline-flex", alignItems: "center" }}>
              {toolbarExtras(editor)}
            </Box>
          </>
        )}
      </Stack>

      {/* Content */}
      <Box
        sx={[
          (theme) => ({
            p: 1.25,
            minHeight,
            fontSize: 13,
            lineHeight: 1.55,
            border: 1,
            borderColor: alpha(theme.palette.text.primary, 0.1),
            borderBottomLeftRadius: 6,
            borderBottomRightRadius: 6,
            "& .ProseMirror": { outline: "none", minHeight: minHeight - 24 },
            "& p": { margin: 0 },
            "& a": { color: theme.palette.primary.main, textDecoration: "underline" },
          }),
          ...(Array.isArray(contentSx) ? contentSx : [contentSx]),
        ]}>
        <EditorContent editor={editor} />
      </Box>

      {/* Link popover */}
      {linkOpen && linkRef.current && (
        <LinkPopover
          editor={editor}
          anchorEl={linkRef.current}
          onClose={() => setLinkOpen(false)}
        />
      )}
    </Box>
  );
}
