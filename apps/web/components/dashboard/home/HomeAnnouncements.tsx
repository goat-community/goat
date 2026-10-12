"use client";

import { useTranslation } from "react-i18next";

import { usePreferences } from "@/lib/api/preferences";
import { useReleases } from "@/lib/api/releases";
import { WELCOME_VIDEO } from "@/lib/constants";

import { useAnnouncementPreview } from "@/hooks/dashboard/home/useAnnouncementPreview";
import { useHomeStage } from "@/hooks/dashboard/home/useHomeStage";
import { useSpotlight } from "@/hooks/dashboard/home/useSpotlight";
import { useWelcome } from "@/hooks/dashboard/home/useWelcome";

import SpotlightModal from "@/components/dashboard/home/SpotlightModal";
import WelcomeDialog from "@/components/dashboard/home/WelcomeDialog";

/**
 * Home's two announcements, one at a time and in order: the first-run Welcome
 * (H7a) first, the release spotlight (H7) only once the Welcome is closed or
 * was never due. The spotlight is held back while the Welcome is open and
 * opens the moment it closes, so a preview of the Welcome on an account with
 * an unseen spotlight sees both, in sequence, never stacked.
 */
const HomeAnnouncements = () => {
  const { i18n } = useTranslation("common");
  const locale = i18n.language === "de" ? "de" : "en";

  const { entries } = useReleases(locale);
  const { preferences } = usePreferences();
  const { stage } = useHomeStage();
  const preview = useAnnouncementPreview();

  // The Welcome is its intro video: without one it never opens, and is never
  // recorded as seen.
  const welcome = useWelcome(stage, preferences, {
    preview: preview.welcome,
    suppress: !WELCOME_VIDEO || Boolean(preview.spotlight),
  });
  const spotlight = useSpotlight(entries, preferences, stage, {
    preview: preview.spotlight,
    suppress: welcome.open,
  });

  if (welcome.open) return <WelcomeDialog onDismiss={welcome.dismiss} />;
  if (spotlight.entry)
    return <SpotlightModal entry={spotlight.entry} onClose={() => void spotlight.dismiss()} />;
  return null;
};

export default HomeAnnouncements;
