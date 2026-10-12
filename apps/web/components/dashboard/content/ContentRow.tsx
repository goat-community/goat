"use client";

import { Box, Chip, Tooltip, Typography, useTheme } from "@mui/material";
import { formatDistance } from "date-fns";
import type { DragEvent } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useDateFnsLocale } from "@/i18n/utils";

import { audienceOf, markKindOf, spaceDisplayName, spaceIconFor, typeLabelKey } from "@/lib/utils/content";
import type { ContentItem, Space } from "@/lib/validations/content";

import type { PopperMenuItem } from "@/components/common/PopperMenu";
import MarkBlock from "@/components/dashboard/common/MarkBlock";
import MetaCell from "@/components/dashboard/common/MetaCell";
import SurfaceCard from "@/components/dashboard/common/SurfaceCard";
import AudienceChip from "@/components/dashboard/content/AudienceChip";
import ContentCreatorCell from "@/components/dashboard/content/ContentCreatorCell";
import ContentKebab from "@/components/dashboard/content/ContentKebab";
import ContentSelectCircle from "@/components/dashboard/content/ContentSelectCircle";

export type ContentRowVariant = "space" | "shared_with_me" | "recent";

interface ContentRowProps {
  item: ContentItem;
  /** The item's home space — the active space while browsing one, or the
   * space `item.space_id` resolves to in a cross-space view. Drives the
   * audience chip and (for "recent") the space-name column. */
  space: Space | undefined;
  /** Which columns render after the name — see the type's doc comment. */
  variant: ContentRowVariant;
  selected: boolean;
  anySelected: boolean;
  onToggleSelect: (id: string) => void;
  onOpen: (item: ContentItem) => void;
  menuItems: PopperMenuItem[];
  onMenuSelect: (item: PopperMenuItem) => void;
  draggable?: boolean;
  onDragStart?: (event: DragEvent<HTMLDivElement>) => void;
  onDragEnd?: (event: DragEvent<HTMLDivElement>) => void;
  /** Only meaningful when `item.type === "folder"` — the list layout
   * renders folders as rows too, so a row doubles as a drop target the same
   * way `ContentFolderCard` does in the grid layout. */
  dragOver?: boolean;
  onDragOverFolder?: (event: DragEvent<HTMLDivElement>) => void;
  onDragLeaveFolder?: (event: DragEvent<HTMLDivElement>) => void;
  onDropFolder?: (event: DragEvent<HTMLDivElement>) => void;
  /** Below `md`: only the select circle, icon, name, and type label render
   * before the kebab — the variant-specific audience/space/role columns
   * don't fit a narrow row and are dropped. The kebab also grows to a 40px
   * tap target. */
  mobile?: boolean;
  /** Renders the hover select circle. Off on Home (H14), where a row is
   * never part of a multi-select. */
  selectable?: boolean;
  /** True only on Home's Recent datasets band (H5/H14), where several rows
   * sit inside one shared `SurfaceCard`. Renders as a plain, borderless strip
   * with a flat hover background instead of the row's own card chrome, so
   * nesting a card inside a card doesn't double the border. */
  flat?: boolean;
  /** Where the item lives, appended to the type line while a search lists
   * results from anywhere beneath the browsed folder. */
  location?: string;
}

/** One list row of the feed: a select circle, a tinted type-icon block, the
 * name with its type label, then columns that depend on which view is showing
 * the row — browsing a space shows who created it, who else can see it and
 * when it changed; "Shared with me" shows who created it, which space it
 * actually lives in and the role you were granted; "Recent" (spanning every
 * space) adds the space column to the space columns — plus the row's kebab
 * menu. The list is where the creator's name is written out; the grid card
 * keeps it in a tooltip. */
const ContentRow = ({
  item,
  space,
  variant,
  selected,
  anySelected,
  onToggleSelect,
  onOpen,
  menuItems,
  onMenuSelect,
  draggable,
  onDragStart,
  onDragEnd,
  dragOver,
  onDragOverFolder,
  onDragLeaveFolder,
  onDropFolder,
  mobile,
  selectable = true,
  flat = false,
  location,
}: ContentRowProps) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const dateLocale = useDateFnsLocale();

  const audience = audienceOf(item, space);
  const spaceName = spaceDisplayName(space, t);
  const isFolder = item.type === "folder";
  const highlighted = selected || (isFolder && !!dragOver);

  const handleClick = (event: { stopPropagation: () => void }) => {
    event.stopPropagation();
    if (anySelected) onToggleSelect(item.id);
    else onOpen(item);
  };

  const rowContent = (
    <>
      {selectable && (
        <ContentSelectCircle
          className="content-row-select"
          checked={selected}
          onToggle={() => onToggleSelect(item.id)}
          mobile={mobile}
        />
      )}

      <MarkBlock kind={markKindOf(item)} geometryType={item.feature_layer_geometry_type} />

      <Box sx={{ flex: "1 1 40%", minWidth: 0 }}>
        <Typography component="div" noWrap title={item.name} sx={{ fontSize: 13.5, fontWeight: 700 }}>
          {item.name}
        </Typography>
        <Typography component="div" noWrap sx={{ fontSize: 11.5, color: theme.palette.text.secondary }}>
          {t(typeLabelKey(item))}
          {item.is_linked && (
            <Tooltip title={t("layer_linked_tip")} placement="top" disableInteractive>
              <Box component="span" sx={{ display: "inline-flex", verticalAlign: "-1px", ml: 1 }}>
                <Icon
                  iconName={ICON_NAME.LINK}
                  style={{ fontSize: 10 }}
                  htmlColor={theme.palette.text.secondary}
                  titleAccess={t("layer_linked")}
                />
              </Box>
            </Tooltip>
          )}
          {location && ` · ${location}`}
        </Typography>
      </Box>

      {!mobile && variant === "space" && (
        <>
          <ContentCreatorCell creator={item.created_by} showName sx={{ width: 140, flexShrink: 0 }} />
          {/* A row states its audience even when nothing is shared: in a
           * list, "Private" is information, and a column that sometimes
           * disappears misaligns every row below it. */}
          <Box sx={{ width: 122, flexShrink: 0, display: "flex" }}>
            <AudienceChip audience={audience} />
          </Box>
          <Tooltip title={t("last_updated")} placement="top" disableInteractive>
            <Typography
              component="span"
              noWrap
              sx={{ width: 112, flexShrink: 0, fontSize: 12.5, color: theme.palette.text.secondary }}>
              {formatDistance(new Date(item.updated_at), new Date(), { addSuffix: true, locale: dateLocale })}
            </Typography>
          </Tooltip>
        </>
      )}

      {!mobile && variant === "shared_with_me" && (
        <>
          <ContentCreatorCell creator={item.created_by} showName sx={{ width: 140, flexShrink: 0 }} />
          <MetaCell icon={spaceIconFor(space)} label={spaceName} sx={{ width: 160, flexShrink: 0 }} />
          <Chip
            label={t(item.my_role)}
            size="small"
            sx={{ height: 18, fontSize: 10, flexShrink: 0, "& .MuiChip-label": { px: 1 } }}
          />
        </>
      )}

      {!mobile && variant === "recent" && (
        <>
          <ContentCreatorCell creator={item.created_by} showName sx={{ width: 140, flexShrink: 0 }} />
          <Box sx={{ width: 122, flexShrink: 0, display: "flex" }}>
            <AudienceChip audience={audience} />
          </Box>
          <MetaCell icon={spaceIconFor(space)} label={spaceName} sx={{ width: 150, flexShrink: 0 }} />
        </>
      )}

      <ContentKebab items={menuItems} onSelect={onMenuSelect} mobile={mobile} />
    </>
  );

  const rowSx = {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "11px 14px",
    cursor: "pointer",
    "&:hover .content-row-select": { opacity: 1 },
  };

  if (flat) {
    return (
      <Box
        onClick={handleClick}
        className="content-row"
        sx={{
          ...rowSx,
          // Rounded so the hover fill reads as an inset block inside the card's
          // own padding, the way the spaces panel's rows do.
          borderRadius: "8px",
          "&:hover": { backgroundColor: theme.palette.action.hover },
        }}>
        {rowContent}
      </Box>
    );
  }

  return (
    <SurfaceCard
      selected={highlighted}
      hoverable={false}
      draggable={draggable}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onDragOver={isFolder ? onDragOverFolder : undefined}
      onDragLeave={isFolder ? onDragLeaveFolder : undefined}
      onDrop={isFolder ? onDropFolder : undefined}
      onClick={handleClick}
      className="content-row"
      sx={rowSx}>
      {rowContent}
    </SurfaceCard>
  );
};

export default ContentRow;
