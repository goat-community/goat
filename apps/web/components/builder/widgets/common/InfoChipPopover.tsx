import { Box, Stack, TextField, Typography } from "@mui/material";
import type { Editor } from "@tiptap/react";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import type { InfoChipPlacement, InfoChipPopupType, InfoChipSize } from "@/lib/extensions/info-chip";

import MarkdownContentEditor from "@/components/builder/widgets/common/MarkdownContentEditor";
import PopupContentRenderer from "@/components/builder/widgets/common/PopupContentRenderer";
import PopupSettingsControls from "@/components/builder/widgets/common/PopupSettingsControls";
import AppDialog, { AppDialogFooter } from "@/components/common/AppDialog";

interface InfoChipEditDialogProps {
  editor: Editor;
  open: boolean;
  onClose: () => void;
  /** Called after the chip's attrs are committed. Lets the host editor flush
   *  any debounced persistence so the new HTML reaches the parent immediately
   *  instead of after the typing-debounce delay. */
  onPersist?: () => void;
}

/**
 * Centered dialog for editing an info chip — type, placement, markdown text, URL all in one view.
 * Replaces the older popover-then-dialog flow.
 */
export const InfoChipEditDialog = ({ editor, open, onClose, onPersist }: InfoChipEditDialogProps) => {
  const { t } = useTranslation("common");

  // Snapshot the chip's position when the dialog opens. The editor selection can
  // shift to a TextSelection between transactions, so we can't rely on
  // `editor.state.selection.from` mid-edit — we'd lose the chip and unmount.
  const [chipPos, setChipPos] = useState<number | null>(null);

  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [popupType, setPopupType] = useState<InfoChipPopupType>("popover");
  const [placement, setPlacement] = useState<InfoChipPlacement>("auto");
  const [size, setSize] = useState<InfoChipSize>("md");

  // Snapshot chip position + initial values when the dialog opens
  useEffect(() => {
    if (!open) return;
    const pos = editor.state.selection.from;
    const node = editor.state.doc.nodeAt(pos);
    if (node?.type.name !== "infoChip") return;
    setChipPos(pos);
    setText((node.attrs.text as string) || "");
    setUrl((node.attrs.url as string) || "");
    setTitle((node.attrs.title as string) || "");
    setPopupType((node.attrs.popup_type as InfoChipPopupType) || "popover");
    setPlacement((node.attrs.placement as InfoChipPlacement) || "auto");
    setSize((node.attrs.size as InfoChipSize) || "md");
    // Snapshot is intentional — only reset when the dialog opens.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // Persist all fields once when the dialog closes. Persisting on every
  // keystroke would cause an editor transaction per character, which triggers
  // re-renders that interrupt typing in the textarea.
  const handleClose = useCallback(() => {
    if (chipPos !== null) {
      let didApply = false;
      editor
        .chain()
        .command(({ tr, state, dispatch }) => {
          const node = state.doc.nodeAt(chipPos);
          if (!node || node.type.name !== "infoChip") return false;
          if (dispatch) {
            tr.setNodeMarkup(chipPos, undefined, {
              ...node.attrs,
              text,
              url,
              title,
              popup_type: popupType,
              placement,
              size,
            });
            didApply = true;
          }
          return true;
        })
        .run();
      if (didApply) onPersist?.();
    }
    onClose();
  }, [editor, chipPos, text, url, title, popupType, placement, size, onClose, onPersist]);

  // Render only when the dialog has captured a chip position. Don't re-check
  // editor.state — the selection may have moved off the chip mid-edit, but the
  // dialog should remain open until the user closes it.
  if (chipPos === null) return null;

  const showUrl = popupType !== "tooltip";
  const showTitle = popupType !== "tooltip";

  return (
    <AppDialog
      open={open}
      onClose={handleClose}
      icon={ICON_NAME.INFO}
      title={t("edit_popup_content")}
      maxWidth={600}
      bodySx={{ pt: 2 }}
      footer={<AppDialogFooter primaryLabel={t("done", { defaultValue: "Done" })} onPrimary={handleClose} />}>
      <Stack spacing={2}>
        <PopupSettingsControls
          popupType={popupType}
          placement={placement}
          size={size}
          onPopupTypeChange={setPopupType}
          onPlacementChange={setPlacement}
          onSizeChange={setSize}
        />

        {showTitle && (
          <Box key="title">
            <Typography
              variant="caption"
              color="text.secondary"
              fontWeight={600}
              sx={{ mb: 0.5, display: "block" }}>
              {t("title")}{" "}
              <Typography component="span" variant="caption" color="text.disabled">
                ({t("optional", { defaultValue: "optional" })})
              </Typography>
            </Typography>
            <TextField
              size="small"
              fullWidth
              placeholder={t("title")}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoComplete="off"
              inputProps={{ "data-testid": "infochip-title-input" }}
            />
          </Box>
        )}

        <Box key="content">
          <Typography
            variant="caption"
            color="text.secondary"
            fontWeight={600}
            sx={{ mb: 0.5, display: "block" }}>
            {t("info_text", { defaultValue: "Info text" })}
          </Typography>
          <MarkdownContentEditor value={text} onChange={setText} plainText={popupType === "tooltip"} />
        </Box>

        {showUrl && (
          <Box key="url">
            <Typography
              variant="caption"
              color="text.secondary"
              fontWeight={600}
              sx={{ mb: 0.5, display: "block" }}>
              {t("link_url", { defaultValue: "Link URL" })}{" "}
              <Typography component="span" variant="caption" color="text.disabled">
                ({t("optional", { defaultValue: "optional" })})
              </Typography>
            </Typography>
            <TextField
              size="small"
              fullWidth
              placeholder="https://..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </Box>
        )}
      </Stack>
    </AppDialog>
  );
};

interface InfoChipViewPopoverProps {
  anchorEl: HTMLElement | null;
  text: string;
  url?: string;
  title?: string;
  popup_type?: InfoChipPopupType;
  placement?: InfoChipPlacement;
  size?: InfoChipSize;
  onClose: () => void;
}

/**
 * Viewer-side popup for an info chip. Switches rendering based on popup_type.
 *
 * The caller is expected to pass a live anchor — either a real DOM element or
 * a virtual element with a `getBoundingClientRect` that re-reads the live chip
 * each call. Don't snapshot the rect here: the chip DOM can be re-created when
 * the underlying html re-renders, and a frozen snapshot would point to a
 * detached node.
 */
export const InfoChipViewPopover = ({
  anchorEl,
  text,
  url,
  title,
  popup_type = "popover",
  placement = "auto",
  size = "md",
  onClose,
}: InfoChipViewPopoverProps) => {
  return (
    <PopupContentRenderer
      open={!!anchorEl}
      onClose={onClose}
      popup_type={popup_type}
      placement={placement}
      size={size}
      anchorEl={anchorEl}
      title={title}
      content={text}
      url={url}
    />
  );
};
