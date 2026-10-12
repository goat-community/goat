"use client";

/**
 * A workflow variable's description, edited from an icon button in its row.
 *
 * The description is longer text than a row has room for, so it opens in a
 * small popover instead. The icon shows whether there is one (muted outline
 * when empty, filled in the primary colour when set) and its tooltip shows the
 * text itself. What is typed is kept when the field loses focus or the
 * popover closes; Escape goes back to the text the popover opened with.
 */
import CommentIcon from "@mui/icons-material/ChatBubble";
import CommentOutlinedIcon from "@mui/icons-material/ChatBubbleOutline";
import { IconButton, Popover, TextField, Tooltip } from "@mui/material";
import React, { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { WORKFLOW_VARIABLE_DESCRIPTION_MAX } from "@/lib/validations/workflow";

interface VariableDescriptionButtonProps {
  value: string | undefined;
  onChange: (description: string) => void;
  /** A validation message for the stored description (e.g. too long). */
  error?: string;
}

export default function VariableDescriptionButton({
  value,
  onChange,
  error,
}: VariableDescriptionButtonProps) {
  const { t } = useTranslation("common");
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  // Synchronous twin of `open`: the field's blur can fire after Escape has
  // closed the popover but before React re-renders, and must not save then.
  const editingRef = useRef(false);
  // The description when the popover opened, which Escape goes back to even
  // if a blur already saved part of the edit.
  const initialRef = useRef("");

  const current = value ?? "";
  const hasDescription = current.trim().length > 0;

  const handleOpen = useCallback(() => {
    setDraft(current);
    initialRef.current = current;
    editingRef.current = true;
    setOpen(true);
  }, [current]);

  const save = useCallback(() => {
    if (!editingRef.current) return;
    if (draft !== current) onChange(draft);
  }, [draft, current, onChange]);

  const handleClose = useCallback(
    (_event: unknown, reason?: "backdropClick" | "escapeKeyDown") => {
      if (reason === "escapeKeyDown") {
        if (current !== initialRef.current) onChange(initialRef.current);
      } else {
        save();
      }
      editingRef.current = false;
      setOpen(false);
    },
    [save, current, onChange]
  );

  const tooltip = error ?? (hasDescription ? current : t("workflow_variable_description_add"));
  const ariaLabel = t(
    hasDescription ? "workflow_variable_description_edit" : "workflow_variable_description_add"
  );

  return (
    <>
      <Tooltip
        title={open ? "" : tooltip}
        placement="top"
        describeChild
        // Long help text reads better as a paragraph than one wide line.
        slotProps={{ tooltip: { sx: { maxWidth: 320, whiteSpace: "pre-line" } } }}>
        <IconButton
          ref={buttonRef}
          size="small"
          aria-label={ariaLabel}
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-invalid={error ? true : undefined}
          data-has-description={hasDescription}
          onClick={handleOpen}
          sx={{
            mt: 0.75,
            color: error ? "error.main" : hasDescription ? "primary.main" : "text.disabled",
            "&:hover": { color: error ? "error.main" : "primary.main" },
          }}>
          {hasDescription ? <CommentIcon fontSize="small" /> : <CommentOutlinedIcon fontSize="small" />}
        </IconButton>
      </Tooltip>
      <Popover
        open={open}
        anchorEl={buttonRef.current}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
        slotProps={{ paper: { sx: { p: 2, width: 340 } } }}>
        <TextField
          autoFocus
          fullWidth
          multiline
          minRows={3}
          maxRows={8}
          size="small"
          label={t("workflow_variable_description")}
          placeholder={t("workflow_variable_description_placeholder")}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={save}
          error={!!error && draft === current}
          helperText={
            error && draft === current ? error : `${draft.length} / ${WORKFLOW_VARIABLE_DESCRIPTION_MAX}`
          }
          FormHelperTextProps={{ sx: { textAlign: error && draft === current ? "left" : "right", mx: 0 } }}
          inputProps={{ maxLength: WORKFLOW_VARIABLE_DESCRIPTION_MAX, style: { fontSize: "0.8125rem" } }}
        />
      </Popover>
    </>
  );
}
