import { Chip, IconButton, Paper, Stack, Tooltip, Typography, useTheme } from "@mui/material";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import type { UploadedAsset } from "@/lib/validations/assets";

import type { PopperMenuItem } from "@/components/common/PopperMenu";
import PopperMenu from "@/components/common/PopperMenu";

interface DocumentCardProps {
  document: UploadedAsset;
  enableActions?: boolean;
  onMenuSelect?: (item: PopperMenuItem, document: UploadedAsset) => void;
}

const MIME_LABEL: Record<string, string> = {
  "application/pdf": "PDF",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
  "application/msword": "DOC",
};

export default function DocumentCard({ document, enableActions, onMenuSelect }: DocumentCardProps) {
  const theme = useTheme();
  const { t } = useTranslation("common");

  const menuItems: PopperMenuItem[] = [
    { id: "delete", label: t("delete"), icon: ICON_NAME.TRASH, color: theme.palette.error.main },
  ];

  const typeLabel = MIME_LABEL[document.mime_type] ?? t("file").toUpperCase();

  return (
    <Tooltip title={document.file_name} placement="top" disableInteractive>
      <Paper
        elevation={0}
        onClick={() => window.open(document.url, "_blank", "noopener,noreferrer")}
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          px: 2,
          py: 1.5,
          width: 190,
          cursor: "pointer",
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 2,
          bgcolor: "background.paper",
          textDecoration: "none",
          "&:hover": { borderColor: "primary.main", bgcolor: "action.hover" },
          transition: "border-color 0.15s, background-color 0.15s",
        }}>
        <Icon
          iconName={ICON_NAME.FILE}
          fontSize="small"
          htmlColor={theme.palette.text.secondary}
        />
        <Stack sx={{ overflow: "hidden", flex: 1, minWidth: 0 }}>
          <Typography variant="body2" noWrap>
            {document.display_name ?? document.file_name}
          </Typography>
          <Chip
            label={typeLabel}
            size="small"
            sx={{
              height: 16,
              fontSize: "9px",
              fontWeight: 500,
              alignSelf: "flex-start",
              "& .MuiChip-label": { px: 0.75 },
            }}
          />
        </Stack>
        {enableActions && onMenuSelect && (
          <PopperMenu
            menuItems={menuItems}
            menuButton={
              <IconButton
                size="small"
                sx={{ ml: "auto", flexShrink: 0 }}>
                <Icon iconName={ICON_NAME.MORE_VERT} style={{ fontSize: 14 }} />
              </IconButton>
            }
            onSelect={(item) => onMenuSelect(item, document)}
          />
        )}
      </Paper>
    </Tooltip>
  );
}
