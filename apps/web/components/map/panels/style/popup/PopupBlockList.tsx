import type { DragEndEvent } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import {
  Box,
  Button,
  Menu,
  MenuItem,
  MenuList,
  Stack,
  Typography,
  useTheme,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { v4 } from "uuid";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import type { PopupBlock } from "@/lib/validations/layer";

import { OverflowTypograpy } from "@/components/common/OverflowTypography";
import { SortableItem } from "@/components/map/panels/style/other/SortableItem";
import SortableWrapper from "@/components/map/panels/style/other/SortableWrapper";

interface BlockTypeMeta {
  value: PopupBlock["type"];
  label: string; // i18n key
  icon: ICON_NAME;
}

// Icons chosen from the available ICON_NAME enum
// (packages/js/ui/components/Icon.tsx).
const BLOCK_TYPES: BlockTypeMeta[] = [
  { value: "text", label: "text_block", icon: ICON_NAME.TEXT },
  { value: "fieldList", label: "field_list", icon: ICON_NAME.LIST },
  { value: "image", label: "image", icon: ICON_NAME.IMAGE },
  { value: "button", label: "button_block", icon: ICON_NAME.LINK },
  { value: "badge", label: "badge_block", icon: ICON_NAME.DATA_CATEGORY },
  { value: "divider", label: "divider_block", icon: ICON_NAME.DIVIDER },
];

/** `buttonLabel` is the default text of a new button block, in the editor's
 * language: it is stored with the block and shown to every popup reader. */
function makeBlock(type: PopupBlock["type"], buttonLabel: string): PopupBlock {
  const id = v4();
  switch (type) {
    case "text":
      return { id, type, html: "" };
    case "fieldList":
      return { id, type, layout: "table", attributes: [], collapse_after: null };
    case "image":
      return {
        id,
        type,
        source: "field",
        sizing: "fixed",
        height: 140,
        aspect: "16/9",
      };
    case "button":
      return { id, type, label: buttonLabel, url_template: "", style: "link" };
    case "badge":
      // `field` is required (.min(1)); user must replace this placeholder
      // before save in the block edit popper.
      return {
        id,
        type,
        field: "placeholder",
        mode: "single",
        palette: {},
        full_width: false,
      };
    case "divider":
      return { id, type, thickness: 1 };
  }
}

interface PopupBlockListProps {
  blocks: PopupBlock[];
  onChange: (next: PopupBlock[]) => void;
  onEdit: (block: PopupBlock, anchorEl: HTMLElement) => void;
  editingId: string | null;
}

export function PopupBlockList({
  blocks,
  onChange,
  onEdit,
  editingId,
}: PopupBlockListProps) {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const [menuAnchor, setMenuAnchor] = useState<HTMLElement | null>(null);

  const handleDragEnd = (e: DragEndEvent) => {
    const from = blocks.findIndex((b) => b.id === e.active.id);
    const to = blocks.findIndex((b) => b.id === e.over?.id);
    if (from === -1 || to === -1 || from === to) return;
    onChange(arrayMove(blocks, from, to));
  };

  return (
    <Box>
      <SortableWrapper handleDragEnd={handleDragEnd} items={blocks}>
        {blocks.map((b) => {
          const meta = BLOCK_TYPES.find((bt) => bt.value === b.type)!;
          return (
            <SortableItem
              key={b.id}
              item={b}
              label={t(meta.label)}
              active={b.id === editingId}
              actions={
                <Icon
                  onClick={() => onChange(blocks.filter((x) => x.id !== b.id))}
                  iconName={ICON_NAME.TRASH}
                  style={{ fontSize: 12, cursor: "pointer" }}
                  htmlColor={theme.palette.text.secondary}
                />
              }>
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                onClick={(e) => onEdit(b, e.currentTarget)}
                sx={{
                  py: 1,
                  cursor: "pointer",
                  "&:hover": { color: "primary.main" },
                }}>
                <Icon iconName={meta.icon} style={{ fontSize: 14 }} htmlColor="inherit" />
                <OverflowTypograpy variant="body2" fontWeight={600}>
                  {t(meta.label)}
                </OverflowTypograpy>
              </Stack>
            </SortableItem>
          );
        })}
      </SortableWrapper>

      <Button
        fullWidth
        variant="text"
        size="small"
        startIcon={<Icon iconName={ICON_NAME.PLUS} style={{ fontSize: 14 }} />}
        onClick={(e) => setMenuAnchor(e.currentTarget)}>
        {t("add_block")}
      </Button>
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        transformOrigin={{ vertical: "top", horizontal: "center" }}
        slotProps={{
          paper: {
            sx: {
              width: menuAnchor ? menuAnchor.offsetWidth : undefined,
              mt: 0.5,
            },
          },
        }}>
        <MenuList dense sx={{ py: 0.5 }}>
          {BLOCK_TYPES.map((bt) => (
            <MenuItem
              key={bt.value}
              onClick={() => {
                onChange([...blocks, makeBlock(bt.value, t("open"))]);
                setMenuAnchor(null);
              }}
              sx={{ py: 0.75, px: 1.5, gap: 1.5 }}>
              <Icon
                iconName={bt.icon}
                style={{ fontSize: 14 }}
                htmlColor={theme.palette.text.secondary}
              />
              <Typography variant="body2" sx={{ fontSize: 13 }}>
                {t(bt.label)}
              </Typography>
            </MenuItem>
          ))}
        </MenuList>
      </Menu>
    </Box>
  );
}
