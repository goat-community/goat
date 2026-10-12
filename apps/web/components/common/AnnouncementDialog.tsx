"use client";

import { Box, Button, Dialog, IconButton, Stack, Typography, useMediaQuery, useTheme } from "@mui/material";
import { type ReactNode, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { youtubeEmbedUrl, youtubePosterUrl, youtubeVideoId } from "@/lib/utils/mediaEmbed";

export type AnnouncementMedia =
  | { kind: "image"; src: string; alt?: string }
  | { kind: "video"; src: string; poster?: string };

export interface AnnouncementAction {
  label: string;
  /** Opens in a new tab; the dialog dismisses as well. */
  href?: string;
  onClick?: () => void;
}

interface AnnouncementDialogProps {
  open: boolean;
  /** A small line above the headline: a section label, or a tag with a date. */
  eyebrow?: ReactNode;
  headline: string;
  /** One entry per paragraph; a node when part of it needs emphasis. */
  body: ReactNode[];
  /** Short bullet points under the body — a release's headline features. */
  highlights?: string[];
  media?: AnnouncementMedia;
  /** The leading button. With `playsVideo` it opens the video in a lightbox instead of dismissing. */
  primary: AnnouncementAction & { playsVideo?: boolean };
  secondary?: AnnouncementAction;
  dismissLabel: string;
  onDismiss: () => void;
}

/** The media pane is dark in both themes; it frames a screenshot the way a launch page does. */
const PANE = { from: "#243040", to: "#18202B" };

/**
 * One announcement, two panes: text on the left with up to three actions,
 * a framed screenshot or a video poster on the right, shown whole. Without media it
 * collapses to a single narrower pane; below `md` the panes stack with the
 * media first. A video plays in a lightbox of its own at viewport size;
 * opening it counts as acting on the announcement, so the announcement goes
 * away and the viewer is back on the page when the video closes.
 *
 * Presentational only: who sees it, when, and what dismissing records is the
 * caller's business (the first-run Welcome and the release spotlight both
 * render through here).
 */
const AnnouncementDialog = ({
  open,
  eyebrow,
  headline,
  body,
  highlights = [],
  media,
  primary,
  secondary,
  dismissLabel,
  onDismiss,
}: AnnouncementDialogProps) => {
  const theme = useTheme();
  const stacked = useMediaQuery(theme.breakpoints.down("md"));
  const titleId = useId();
  const [playing, setPlaying] = useState(false);

  const act = (action: AnnouncementAction) => {
    action.onClick?.();
    onDismiss();
  };

  const actionProps = (action: AnnouncementAction) =>
    action.href
      ? { component: "a" as const, href: action.href, target: "_blank", rel: "noopener noreferrer" }
      : {};

  const play = () => {
    primary.onClick?.();
    setPlaying(true);
  };

  const closeVideo = () => {
    setPlaying(false);
    onDismiss();
  };

  return (
    <>
      <Dialog
        open={open && !playing}
        onClose={onDismiss}
        maxWidth={false}
        aria-labelledby={titleId}
        PaperProps={{
          sx: {
            width: media ? 900 : 560,
            maxWidth: "calc(100vw - 32px)",
            borderRadius: "12px",
            overflow: "hidden",
          },
        }}>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: media && !stacked ? "minmax(0, 2fr) minmax(0, 3fr)" : "1fr",
            minHeight: media && !stacked ? 460 : undefined,
          }}>
          {media && stacked && <MediaPane media={media} onPlay={play} stacked />}
          <Stack spacing={2.5} sx={{ p: stacked ? "24px 20px 20px" : "40px 36px 32px" }}>
            {eyebrow}
            <Typography
              id={titleId}
              component="h2"
              sx={{
                fontSize: stacked || !media ? 22 : 28,
                fontWeight: 800,
                lineHeight: 1.15,
                letterSpacing: "-0.01em",
              }}>
              {headline}
            </Typography>
            <Stack spacing={2.5} sx={{ flex: 1, pt: 3 }}>
              {body.map((paragraph, index) => (
                <Typography key={index} variant="body2" color="text.secondary" sx={{ lineHeight: 1.55 }}>
                  {paragraph}
                </Typography>
              ))}
              {highlights.length > 0 && (
                <Box component="ul" sx={{ m: 0, pl: 4.5, display: "grid", gap: 1 }}>
                  {highlights.map((highlight, index) => (
                    <Typography key={index} component="li" variant="body2" sx={{ lineHeight: 1.5 }}>
                      {highlight}
                    </Typography>
                  ))}
                </Box>
              )}
            </Stack>
            <Stack direction="row" alignItems="center" spacing={3} flexWrap="wrap" useFlexGap sx={{ pt: 2 }}>
              {primary.playsVideo && media?.kind === "video" ? (
                <Button
                  variant="contained"
                  startIcon={<Icon iconName={ICON_NAME.PLAY} style={{ fontSize: 13 }} />}
                  onClick={play}>
                  {primary.label}
                </Button>
              ) : (
                <Button variant="contained" {...actionProps(primary)} onClick={() => act(primary)}>
                  {primary.label}
                </Button>
              )}
              {secondary && (
                <Button variant="text" {...actionProps(secondary)} onClick={() => act(secondary)}>
                  {secondary.label}
                </Button>
              )}
              <Button variant="text" color="inherit" sx={{ color: "text.secondary" }} onClick={onDismiss}>
                {dismissLabel}
              </Button>
            </Stack>
          </Stack>
          {media && !stacked && <MediaPane media={media} onPlay={play} />}
        </Box>
      </Dialog>
      {media?.kind === "video" && <VideoLightbox media={media} open={playing} onClose={closeVideo} />}
    </>
  );
};

/** The poster to show for a piece of media before anything plays. */
const posterOf = (media: AnnouncementMedia): string | undefined => {
  if (media.kind === "image") return media.src;
  if (media.poster) return media.poster;
  const youtube = youtubeVideoId(media.src);
  return youtube ? youtubePosterUrl(youtube) : undefined;
};

const MediaPane = ({
  media,
  onPlay,
  stacked = false,
}: {
  media: AnnouncementMedia;
  onPlay: () => void;
  stacked?: boolean;
}) => {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const poster = posterOf(media);
  const video = media.kind === "video";

  return (
    <Box
      sx={{
        background: `radial-gradient(120% 100% at 100% 0%, ${PANE.from}, ${PANE.to} 70%)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: stacked ? 0 : "34px",
        overflow: "hidden",
      }}>
      {/* The whole frame, never a crop: a screenshot or poster is shown as
          the author composed it, letterboxed on the dark frame if its
          ratio differs from 16:9. */}
      <Box
        sx={{
          position: "relative",
          width: "100%",
          aspectRatio: "16 / 9",
          borderRadius: stacked ? 0 : "10px",
          overflow: "hidden",
          backgroundColor: "#0B1017",
          boxShadow: stacked ? "none" : "0 18px 50px rgba(0,0,0,.45)",
        }}>
        {poster && (
          <Box
            component="img"
            src={poster}
            alt={media.kind === "image" ? (media.alt ?? "") : ""}
            sx={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
          />
        )}
        {video && (
          <IconButton
            aria-label={t("play")}
            onClick={onPlay}
            sx={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              borderRadius: 0,
              background: "linear-gradient(180deg, rgba(0,0,0,.05), rgba(0,0,0,.35))",
              "&:hover": { background: "linear-gradient(180deg, rgba(0,0,0,.1), rgba(0,0,0,.4))" },
              "&:hover .play-disc": { transform: "scale(1.06)" },
            }}>
            <Box
              className="play-disc"
              sx={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                backgroundColor: theme.palette.primary.main,
                display: "grid",
                placeItems: "center",
                boxShadow: "0 8px 24px rgba(0,0,0,.35)",
                transition: theme.transitions.create("transform", { duration: 150 }),
              }}>
              <Icon iconName={ICON_NAME.PLAY} htmlColor="#fff" style={{ fontSize: 24, marginLeft: 4 }} />
            </Box>
          </IconButton>
        )}
      </Box>
    </Box>
  );
};

/**
 * The video at viewport size, black surround, one close button above the
 * frame. Opened by a click, so it starts on its own with sound.
 */
const VideoLightbox = ({
  media,
  open,
  onClose,
}: {
  media: Extract<AnnouncementMedia, { kind: "video" }>;
  open: boolean;
  onClose: () => void;
}) => {
  const { t } = useTranslation("common");
  const youtube = youtubeVideoId(media.src);
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={false}
      aria-label={t("video")}
      PaperProps={{
        sx: {
          width: "min(1280px, calc(100vw - 48px))",
          maxWidth: "none",
          // Room above the frame for the close button, which sits outside the
          // video so it never lands on the recording's own controls.
          mt: "56px",
          backgroundColor: "transparent",
          backgroundImage: "none",
          boxShadow: "none",
          overflow: "visible",
        },
      }}>
      <IconButton
        aria-label={t("close")}
        onClick={onClose}
        sx={{
          position: "absolute",
          top: -48,
          right: 0,
          width: 40,
          height: 40,
          color: "#fff",
          backgroundColor: "rgba(255,255,255,.12)",
          "&:hover": { backgroundColor: "rgba(255,255,255,.22)" },
        }}>
        <Icon iconName={ICON_NAME.XCLOSE} style={{ fontSize: 16 }} />
      </IconButton>
      <Box
        sx={{
          position: "relative",
          aspectRatio: "16 / 9",
          backgroundColor: "#000",
          borderRadius: "12px",
          overflow: "hidden",
          boxShadow: "0 24px 80px rgba(0,0,0,.6)",
        }}>
        {open &&
          (youtube ? (
            <Box
              component="iframe"
              src={youtubeEmbedUrl(youtube, { muted: false })}
              title={media.src}
              allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
              allowFullScreen
              sx={{ position: "absolute", inset: 0, width: "100%", height: "100%", border: 0 }}
            />
          ) : (
            <Box
              component="video"
              src={media.src}
              poster={media.poster}
              autoPlay
              controls
              playsInline
              sx={{ position: "absolute", inset: 0, width: "100%", height: "100%", display: "block" }}
            />
          ))}
      </Box>
    </Dialog>
  );
};

export default AnnouncementDialog;
