"use client";

import { Alert, Box, Button, IconButton, Stack, Typography, alpha, useTheme } from "@mui/material";
import type { ReactNode } from "react";
import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { checkFiles } from "@/lib/support/files";

type Props = { files: File[]; onChange: (files: File[]) => void; compact?: boolean };

const reasonKey = {
  too_many_files: "support_too_many_files",
  file_too_large: "support_file_too_large",
  files_too_large: "support_files_too_large",
} as const;

const isImage = (name: string) => /\.(png|jpe?g|gif|webp|svg)$/i.test(name);

/** A picked or attached file as a small rounded tag: type glyph, name, then whatever follows (size, remove). */
export const FileTag = ({
  name,
  children,
  onClick,
}: {
  name: string;
  children?: ReactNode;
  onClick?: () => void;
}) => {
  const theme = useTheme();
  return (
    <Box
      component={onClick ? "button" : "span"}
      type={onClick ? "button" : undefined}
      onClick={onClick}
      sx={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        maxWidth: "100%",
        minHeight: 30,
        boxSizing: "border-box",
        pl: "10px",
        pr: children ? "4px" : "10px",
        py: "4px",
        borderRadius: "8px",
        border: `1px solid ${theme.palette.divider}`,
        backgroundColor: theme.palette.background.paper,
        font: "inherit",
        fontSize: 12,
        fontWeight: 600,
        color: theme.palette.text.primary,
        cursor: onClick ? "pointer" : "default",
        ...(onClick && {
          "&:hover": {
            borderColor: alpha(theme.palette.text.primary, 0.24),
            backgroundColor: theme.palette.action.hover,
          },
        }),
      }}>
      <Icon
        iconName={isImage(name) ? ICON_NAME.IMAGE : ICON_NAME.FILE}
        style={{ fontSize: 12, flexShrink: 0 }}
        htmlColor={theme.palette.text.secondary}
      />
      <Box
        component="span"
        sx={{ minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {name}
      </Box>
      {children}
    </Box>
  );
};

/** Choose several files at once; enforces 10 files / 10 MB each / 50 MB per message. */
const FilePicker = ({ files, onChange, compact }: Props) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const input = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const add = (picked: File[]) => {
    if (picked.length === 0) return;
    const next = [...files, ...picked];
    const check = checkFiles(next);
    if (!check.ok) {
      setError(t(reasonKey[check.reason], { name: check.name }));
      return;
    }
    setError(null);
    onChange(next);
  };
  const chooseButton = (
    <Button
      size="small"
      variant="text"
      onClick={() => input.current?.click()}
      startIcon={compact ? <Icon iconName={ICON_NAME.UPLOAD} style={{ fontSize: 13 }} /> : undefined}
      sx={{ textTransform: "none", fontWeight: 700 }}>
      {t("support_choose_files")}
    </Button>
  );
  return (
    <Stack spacing="8px">
      <input
        ref={input}
        type="file"
        multiple
        hidden
        data-testid="support-file-input"
        onChange={(e) => {
          // Copy first: clearing the value empties the live FileList. Clearing lets the same file be picked again.
          const picked = Array.from(e.target.files ?? []);
          e.target.value = "";
          add(picked);
        }}
      />
      <Box
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          add(Array.from(e.dataTransfer.files));
        }}
        sx={
          compact
            ? {}
            : {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                border: `1px dashed ${alpha(theme.palette.text.primary, 0.24)}`,
                borderRadius: "10px",
                px: 2,
                py: "10px",
              }
        }>
        {!compact && (
          <Icon
            iconName={ICON_NAME.UPLOAD}
            style={{ fontSize: 15 }}
            htmlColor={theme.palette.text.secondary}
          />
        )}
        {chooseButton}
      </Box>
      {files.length > 0 && (
        <Stack direction="row" flexWrap="wrap" gap="6px">
          {files.map((f, i) => (
            <FileTag key={`${f.name}-${i}`} name={f.name}>
              <Typography
                component="span"
                sx={{ fontSize: 11.5, color: "text.secondary", whiteSpace: "nowrap" }}>
                {Math.max(1, Math.round(f.size / 1024))} KB
              </Typography>
              <IconButton
                size="small"
                aria-label={`${t("support_remove")} ${f.name}`}
                onClick={() => onChange(files.filter((_, j) => j !== i))}
                sx={{ width: 22, height: 22 }}>
                <Icon iconName={ICON_NAME.XCLOSE} style={{ fontSize: 10 }} />
              </IconButton>
            </FileTag>
          ))}
        </Stack>
      )}
      {error && (
        <Alert severity="error" onClose={() => setError(null)}>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      )}
    </Stack>
  );
};

export default FilePicker;
