"use client";

import { Box, Typography } from "@mui/material";
import type { DragEvent } from "react";

import { audienceOf } from "@/lib/utils/content";
import type { ContentItem, Space } from "@/lib/validations/content";

import type { PopperMenuItem } from "@/components/common/PopperMenu";
import MarkBlock from "@/components/dashboard/common/MarkBlock";
import SurfaceCard from "@/components/dashboard/common/SurfaceCard";
import AudienceChip from "@/components/dashboard/content/AudienceChip";
import ContentKebab from "@/components/dashboard/content/ContentKebab";
import ContentSelectCircle from "@/components/dashboard/content/ContentSelectCircle";

interface ContentFolderCardProps {
  item: ContentItem;
  space: Space | undefined;
  selected: boolean;
  anySelected: boolean;
  onToggleSelect: (id: string) => void;
  onOpen: (item: ContentItem) => void;
  menuItems: PopperMenuItem[];
  onMenuSelect: (item: PopperMenuItem) => void;
  /** A folder is itself draggable (owner only) as well as a drop target —
   * the drag-start props below move the folder card itself; the drag-over/
   * leave/drop props below accept another item being dropped onto it. */
  draggable?: boolean;
  onDragStart?: (event: DragEvent<HTMLDivElement>) => void;
  onDragEnd?: (event: DragEvent<HTMLDivElement>) => void;
  /** Whether a drag is currently hovering this folder as a drop target. */
  dragOver?: boolean;
  onDragOverFolder?: (event: DragEvent<HTMLDivElement>) => void;
  onDragLeaveFolder?: (event: DragEvent<HTMLDivElement>) => void;
  onDropFolder?: (event: DragEvent<HTMLDivElement>) => void;
  /** Below `md`: a larger 28px select circle and a 40px kebab tap target,
   * matching `ContentCard`'s mobile sizing so the grid reads consistently. */
  mobile?: boolean;
  /** Where the folder lives, shown under its name while a search lists
   * folders from anywhere beneath the browsed one. */
  location?: string;
  /** Renders the hover select circle. Off where a folder is navigated but
   * never selected, as in the dataset picker. */
  selectable?: boolean;
}

/** A folder tile: a tinted icon block, the name, and — since the feed carries
 * no item count for a folder — an audience chip in place of the "N items"
 * caption other tools show. Doubles as a drop target for drag-to-move. */
const ContentFolderCard = ({
  item,
  space,
  selected,
  anySelected,
  onToggleSelect,
  onOpen,
  location,
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
}: ContentFolderCardProps) => {
  const audience = audienceOf(item, space);
  const showAudience =
    audience.kind === "public" ||
    audience.kind === "restricted" ||
    audience.kind === "shared" ||
    audience.kind === "org";
  const highlighted = dragOver || selected;

  return (
    <SurfaceCard
      selected={highlighted}
      draggable={draggable}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onClick={(event) => {
        event.stopPropagation();
        if (anySelected) onToggleSelect(item.id);
        else onOpen(item);
      }}
      onDragOver={onDragOverFolder}
      onDragLeave={onDragLeaveFolder}
      onDrop={onDropFolder}
      className="content-card"
      sx={{
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        gap: "12px",
        padding: "14px 10px 14px 16px",
        "&:hover .content-card-select": { opacity: 1 },
      }}>
      <MarkBlock kind="folder" size={38} />

      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
        <Typography component="div" noWrap title={item.name} sx={{ fontSize: 14.5, fontWeight: 700 }}>
          {item.name}
        </Typography>
        {location && (
          <Typography component="div" noWrap sx={{ fontSize: 11.5, color: "text.secondary" }}>
            {location}
          </Typography>
        )}
        {showAudience && (
          <Box sx={{ mt: "2px", display: "flex", alignItems: "center", gap: "7px" }}>
            <AudienceChip audience={audience} />
          </Box>
        )}
      </Box>

      {selectable && (
        <ContentSelectCircle
          className="content-card-select"
          checked={selected}
          onToggle={() => onToggleSelect(item.id)}
          mobile={mobile}
        />
      )}
      <ContentKebab items={menuItems} onSelect={onMenuSelect} mobile={mobile} />
    </SurfaceCard>
  );
};

export default ContentFolderCard;
