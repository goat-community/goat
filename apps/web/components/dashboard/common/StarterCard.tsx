"use client";

import { Box, IconButton, Tooltip, Typography, alpha, useTheme } from "@mui/material";
import { formatDistanceToNowStrict } from "date-fns";
import { useTranslation } from "react-i18next";

import { GOATLogoIconOnlyGreen } from "@p4b/ui/assets/svg/GOATLogoIconOnlyGreen";
import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useDateFnsLocale } from "@/i18n/utils";

import { layoutPageDescription } from "@/lib/templates/previewGeometry";
import type { TemplateRead } from "@/lib/validations/template";

import ContentThumbnail from "@/components/dashboard/common/ContentThumbnail";
import KindBadges from "@/components/dashboard/common/KindBadges";
import SurfaceCard from "@/components/dashboard/common/SurfaceCard";
import TypeTag from "@/components/dashboard/common/TypeTag";
import ContentCreatorCell from "@/components/dashboard/content/ContentCreatorCell";
import TemplateDefaultThumbnail, {
  hasTemplateDefaultThumbnail,
} from "@/components/templates/TemplateDefaultThumbnail";
import TemplateTag from "@/components/templates/TemplateTag";

const THUMBNAIL_HEIGHT = 132;
/** The height `ContentCard` gives its title row, where a 28px kebab (40px on
 * a phone) sits beside the name. This card carries no kebab, so it holds the
 * same row height itself — a template tile and a project tile sit in the same
 * grids, and the name, the meta row under it and the card's own height have to
 * land in the same places on both. */
const TITLE_ROW_HEIGHT = 28;
const TITLE_ROW_HEIGHT_MOBILE = 40;
/** How much of the meta row a category tag may take. A category is a name the
 * author typed, so an unbounded one would eat the creator and the time; capped,
 * `TemplateTag`'s own ellipsis cuts it and its `title` keeps the full spelling. */
const CATEGORY_TAG_MAX_WIDTH = 90;
/** `UserAvatar`'s own default, so the stand-in avatar beside it is the same
 * circle and the meta row keeps its height. */
const AVATAR_SIZE = 22;
/** The gap `ContentCreatorCell` keeps between the avatar and the name. */
const AVATAR_GAP = 7;
/** What the creator's name needs before it reads as a name rather than as a
 * sliver. It is the floor the cell may shrink to, never a fixed width. */
const CREATOR_NAME_MIN = 56;

/**
 * How wide the card has to be before a category may take any of the meta
 * row, and how wide before even the bare count may. The row is the card less
 * the body's 22px of side padding and its 4px right inset: the 22px avatar,
 * the 7px gap, the 56px the name needs, two 8px gaps and ~63px for the
 * relative time — about 158px before a category is even considered, so a
 * useful ~48px tag wants a 233px card and the 26px count a 219px one.
 *
 * Both are container queries on the card, not viewport breakpoints: the
 * constraint is the card's own width, and the same card is 212px in the Home
 * band and ~250px in the Catalog grid at one and the same viewport. An
 * `inline-size` container answers for its content box, so these are 2px
 * inside the card's own width — its borders.
 */
const CATEGORY_TAG_MIN_CARD = 233;
const CATEGORY_COUNT_MIN_CARD = 219;
/** The container these queries measure — named, so nothing else on the page
 * can answer them. */
const CARD_CONTAINER = "starter-card";

/** The corner the categories sit in: pushed to the right end of the meta
 * row, where a content card carries its audience chip. */
const CATEGORY_GROUP_SX = {
  display: "flex",
  alignItems: "center",
  gap: "4px",
  flexShrink: 0,
  ml: "auto",
} as const;

/** The categories a card has no room to spell out, as a count with their
 * names in its tooltip, in the muted tone: it names no category of its own,
 * so it takes no category's colour. A `span` holds the tooltip's ref, which
 * `TemplateTag` does not forward. */
const CategoryMarker = ({ names }: { names: string[] }) => (
  <Tooltip title={names.join(", ")} placement="top" disableInteractive>
    <Box component="span" sx={{ display: "inline-flex", flexShrink: 0 }}>
      <TemplateTag label={`+${names.length}`} />
    </Box>
  </Tooltip>
);

/** What stands in for a creator's avatar on a seeded starter, whose source is
 * GOAT itself rather than a person: the GOAT mark in the circle `UserAvatar`
 * draws, on a tint of the same brand green the mark is drawn in — legible on
 * the card's surface in both themes, where a bare glyph would read as loose
 * decoration rather than as an avatar. */
const GoatSourceAvatar = () => {
  const theme = useTheme();

  return (
    <Box
      data-testid="template-source-avatar"
      sx={{
        width: AVATAR_SIZE,
        height: AVATAR_SIZE,
        flexShrink: 0,
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: alpha(theme.palette.primary.main, theme.palette.mode === "dark" ? 0.26 : 0.14),
      }}>
      <GOATLogoIconOnlyGreen style={{ width: 13, height: 13 }} />
    </Box>
  );
};

interface StarterCardProps {
  template: TemplateRead;
  /** Renders the top-right pin filled and always visible; unset (rather
   * than pinned=false) hides the pin control entirely, same as
   * `ContentCard`'s `onTogglePin`. */
  pinned?: boolean;
  onTogglePin?: () => void;
  onOpen: () => void;
  /** Below `md`: a shorter 96px thumbnail, matching `ContentCard`'s split. */
  mobile?: boolean;
}

/** The template browser/Home band's card (T7/§4): the template's picture —
 * its thumbnail where it has one, else the template mark every other
 * content type falls back to — carrying the kind badges, the "Sample data"
 * scrim and, for a layout, the page it prints on; paper below with the name
 * and one meta row, the same one `ContentCard` renders — the creator, the
 * last-updated time, and in the right-hand corner the categories, where a
 * content card carries its audience. One family with `ContentCard`, trimmed
 * to what a template card needs — no select circle or kebab, since the
 * browser is a picker, not a content list. */
const StarterCard = ({ template, pinned, onTogglePin, onOpen, mobile }: StarterCardProps) => {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const dateLocale = useDateFnsLocale();
  const thumbnailHeight = mobile ? 96 : THUMBNAIL_HEIGHT;

  const categories = template.categories ?? [];
  /** At most one category is ever spelled out; the rest are a count with
   * their names in its tooltip. How much of that the card can actually hold
   * is a container query below, not a decision taken here. */
  const restCategories = categories.slice(1);
  /** A layout template's page, tagged on the picture — the same
   * "A4 · Landscape" its preview and its browser row carry. */
  const page = layoutPageDescription(template, t);

  return (
    <SurfaceCard
      onClick={onOpen}
      sx={{
        cursor: "pointer",
        display: "flex",
        flexDirection: "column",
        // The meta row's contents are decided by how wide the card is, so the
        // card is what its own queries measure.
        containerType: "inline-size",
        containerName: CARD_CONTAINER,
        "&:hover .starter-card-pin": { opacity: 1 },
      }}>
      <Box
        sx={{
          position: "relative",
          height: thumbnailHeight,
          borderBottom: `1px solid ${theme.palette.divider}`,
          borderRadius: "11px 11px 0 0",
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          // `ContentThumbnail` rounds its own frame; the card's clipped top
          // corners already do that.
          "& > div:first-of-type": { borderRadius: 0 },
        }}>
        <ContentThumbnail
          kind="template"
          href={template.thumbnail_url ?? undefined}
          variant="card"
          height={thumbnailHeight}
          fallback={
            // No picture: the default its payload kind draws — a blank page in
            // the orientation a layout prints on, a step chain for a
            // workflow. A project has none, and keeps the template mark.
            hasTemplateDefaultThumbnail(template.payload_kind) ? (
              <TemplateDefaultThumbnail payloadKind={template.payload_kind} page={page} variant="card" />
            ) : undefined
          }
        />
        <Box sx={{ position: "absolute", top: 10, left: 10 }}>
          <KindBadges kinds={template.kinds ?? []} />
        </Box>
        {/* One marker in the bottom-left corner: shipped data, or the page a
            layout prints on. The two cannot both apply — data comes from
            shipped input layers, which only a workflow or project payload
            has, and the page only a layout payload. */}
        {(template.ships_data || page) && (
          <Box sx={{ position: "absolute", bottom: 8, left: 8 }}>
            <TypeTag label={template.ships_data ? t("includes_data") : (page?.label ?? "")} />
          </Box>
        )}
      </Box>

      {onTogglePin && (
        <Box sx={{ position: "absolute", top: 8, right: 8 }}>
          <Tooltip title={t(pinned ? "unpin_from_home" : "pin_to_home")} placement="top" disableInteractive>
            <IconButton
              className="starter-card-pin"
              aria-label={t(pinned ? "unpin_from_home" : "pin_to_home")}
              onClick={(event) => {
                event.stopPropagation();
                onTogglePin();
              }}
              sx={{
                width: 26,
                height: 26,
                p: 0,
                borderRadius: "50%",
                backgroundColor: theme.palette.background.paper,
                opacity: pinned ? 1 : 0,
                transition: "opacity 120ms",
                "&:hover": { backgroundColor: theme.palette.background.paper },
              }}>
              <Icon
                iconName={ICON_NAME.BOOKMARK}
                style={{
                  fontSize: 14,
                  color: pinned ? theme.palette.primary.main : theme.palette.text.secondary,
                }}
              />
            </IconButton>
          </Tooltip>
        </Box>
      )}

      <Box sx={{ padding: "9px 9px 12px 13px" }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            minHeight: mobile ? TITLE_ROW_HEIGHT_MOBILE : TITLE_ROW_HEIGHT,
          }}>
          <Typography
            component="div"
            noWrap
            sx={{
              flex: 1,
              minWidth: 0,
              fontSize: 14,
              fontWeight: 700,
              letterSpacing: "-0.1px",
              lineHeight: 1.3,
            }}>
            {template.name}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: "8px", mt: "4px", pr: "4px" }}>
          {/* A seeded starter has no creating account, so the cell falls back
              to GOAT itself — the same row, so the card's rhythm holds
              whether or not a person made the template. */}
          <ContentCreatorCell
            creator={template.created_by}
            showName
            fallbackName={t("source_goat")}
            fallbackAvatar={<GoatSourceAvatar />}
            // A floor, not a width: the name shrinks with the row but never
            // past what makes it readable, so a category can never squeeze it
            // to a sliver.
            sx={{ minWidth: AVATAR_SIZE + AVATAR_GAP + CREATOR_NAME_MIN }}
          />
          <Tooltip title={t("last_updated")} placement="top" disableInteractive>
            <Typography
              component="span"
              noWrap
              sx={{ fontSize: 12, color: theme.palette.text.secondary, flexShrink: 0 }}>
              {/* The strict, floored distance ("3 hours ago", not "about 3
               * hours ago") — the meta row is one line at the card's
               * minimum width, the same as on `ContentCard`. */}
              {formatDistanceToNowStrict(new Date(template.updated_at), {
                addSuffix: true,
                roundingMethod: "floor",
                locale: dateLocale,
              })}
            </Typography>
          </Tooltip>
          {categories.length > 0 &&
            (mobile ? (
              // A phone's card never spells a category out: it carries the
              // count alone, and only on a card wide enough to hold it after
              // the name and the time. The full list is in the preview dialog.
              <Box
                data-testid="template-category-count"
                sx={{
                  ...CATEGORY_GROUP_SX,
                  display: "none",
                  [`@container ${CARD_CONTAINER} (min-width: ${CATEGORY_COUNT_MIN_CARD}px)`]: {
                    display: "flex",
                  },
                }}>
                <CategoryMarker names={categories} />
              </Box>
            ) : (
              <>
                {/* One category spelled out, and a count for the rest — only
                    on a card wide enough to hold it after the name and the
                    time have had theirs. */}
                <Box
                  data-testid="template-category-tags"
                  sx={{
                    ...CATEGORY_GROUP_SX,
                    display: "none",
                    // The one item in the row that gives space back: past its
                    // threshold the tag takes what is left over and ellipsises,
                    // so it can never push the time out of the row.
                    flexShrink: 1,
                    minWidth: 0,
                    [`@container ${CARD_CONTAINER} (min-width: ${CATEGORY_TAG_MIN_CARD}px)`]: {
                      display: "flex",
                    },
                  }}>
                  {/* The tag is capped, and shrinks with what is left, so its
                      own ellipsis cuts a long category instead of the row
                      eating the creator and the time. `TemplateTag` keeps the
                      full spelling in its `title`. */}
                  <Box
                    component="span"
                    sx={{
                      display: "inline-flex",
                      minWidth: 0,
                      maxWidth: CATEGORY_TAG_MAX_WIDTH,
                      overflow: "hidden",
                    }}>
                    <TemplateTag label={categories[0]} tone="category" />
                  </Box>
                  {restCategories.length > 0 && <CategoryMarker names={restCategories} />}
                </Box>
                {/* Too narrow to spell one out, wide enough for the count:
                    every category collapses into the marker. Hidden from the
                    reader that is not looking at it — whichever of the two
                    renderings the card is too narrow for is `display: none`,
                    and only one is ever on screen. */}
                <Box
                  aria-hidden
                  data-testid="template-category-count"
                  sx={{
                    ...CATEGORY_GROUP_SX,
                    display: "none",
                    [`@container ${CARD_CONTAINER} (min-width: ${CATEGORY_COUNT_MIN_CARD}px) and (max-width: ${CATEGORY_TAG_MIN_CARD - 1}px)`]:
                      { display: "flex" },
                  }}>
                  <CategoryMarker names={categories} />
                </Box>
              </>
            ))}
        </Box>
      </Box>
    </SurfaceCard>
  );
};

export default StarterCard;
