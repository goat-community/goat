"use client";

import { Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { WELCOME_VIDEO } from "@/lib/constants";

import AnnouncementDialog from "@/components/common/AnnouncementDialog";

/**
 * The first-run Welcome: one screen with the intro video. Who sees it and
 * when is `useWelcome`'s business, orchestrated by `HomeAnnouncements`;
 * "Watch video" plays in a lightbox, "Skip guide" hands over to the
 * onboarding checklist underneath. Renders nothing where no intro video is
 * configured (`WELCOME_VIDEO`).
 */
const WelcomeDialog = ({ onDismiss }: { onDismiss: () => void }) => {
  const { t } = useTranslation("common");

  if (!WELCOME_VIDEO) return null;

  return (
    <AnnouncementDialog
      open
      eyebrow={
        <Typography
          component="span"
          sx={{ fontSize: 11, fontWeight: 800, letterSpacing: "0.08em", textTransform: "uppercase" }}
          color="primary">
          {t("getting_started")}
        </Typography>
      }
      headline={t("welcome_dialog_title")}
      body={[
        <>
          <Typography component="span" variant="body2" sx={{ fontWeight: 700, color: "text.primary" }}>
            {t("welcome_dialog_lead")}
          </Typography>{" "}
          {t("welcome_dialog_body_1")}
        </>,
      ]}
      media={{ kind: "video", src: WELCOME_VIDEO.url, poster: WELCOME_VIDEO.poster }}
      primary={{ label: t("watch_video"), playsVideo: true }}
      dismissLabel={t("skip_guide")}
      onDismiss={onDismiss}
    />
  );
};

export default WelcomeDialog;
