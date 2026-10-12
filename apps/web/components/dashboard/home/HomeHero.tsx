"use client";

import { Box, Button, Skeleton, Typography, useTheme } from "@mui/material";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import type { HomeStage } from "@/hooks/dashboard/home/useHomeStage";

import { addLayerSource } from "@/components/addLayer/sources";
import { NewProjectButton } from "@/components/dashboard/common/NewProjectMenu";
import HelpStrip from "@/components/dashboard/home/HelpStrip";

// The Upload dataset quick action, labelled and drawn as in the Add layer menu.
const uploadSource = addLayerSource("upload");

interface HomeHeroProps {
  stage: HomeStage;
  firstName: string;
  /** The ⌘K hero search field, rendered by the caller (`HomeSearch`, mounted by `HomePage`). */
  search: ReactNode;
  /** The caller's personal home folder — where a blank project created from
   * the hero lands, Home having no folder of its own being browsed. */
  homeFolderId?: string;
  onAddDataset: () => void;
  onBrowseCatalog: () => void;
  /** The greeting and subtitle become skeletons while the profile or the
   * stage is still in flight; search and the quick actions still render, so
   * the hero does not shift once they arrive. */
  loading?: boolean;
  /** H12: false once the caller has reached Established. */
  showHelp: boolean;
  mobile: boolean;
}

/**
 * The top of Home: greeting ("Welcome to GOAT" until the caller is
 * Established — a caller leaves New the moment their first project exists,
 * often in the same sitting, so only Established is "back"), then —
 * everywhere except New, where there is
 * nothing yet to search for or act on — the search slot and the quick
 * actions (H11), and finally the help strip (H12). All three bands are
 * driven by the same per-caller stage, which is why they live in one
 * component rather than three siblings in `HomePage`.
 */
const HomeHero = ({
  stage,
  firstName,
  search,
  homeFolderId,
  onAddDataset,
  onBrowseCatalog,
  loading,
  showHelp,
  mobile,
}: HomeHeroProps) => {
  const { t } = useTranslation("common");
  const theme = useTheme();

  const quickActionSx = {
    borderRadius: "999px",
    textTransform: "none" as const,
    fontWeight: 600,
    px: "18px",
    boxShadow: "none",
    "&:hover": { boxShadow: "none" },
  };

  return (
    <Box component="header">
      {loading ? (
        <>
          <Skeleton
            variant="text"
            width={mobile ? 220 : 340}
            sx={{ mx: "auto", fontSize: mobile ? 22 : 30 }}
          />
          <Skeleton variant="text" width={280} sx={{ mx: "auto", mt: "6px", fontSize: 14.5 }} />
        </>
      ) : (
        <>
          <Typography
            component="h1"
            sx={{
              textAlign: "center",
              fontSize: mobile ? 22 : 30,
              fontWeight: 600,
              letterSpacing: "-0.3px",
            }}>
            {stage === "established"
              ? t("welcome_back", { name: firstName })
              : t("welcome_to_goat", { name: firstName })}
          </Typography>
          <Typography
            sx={{ mt: "6px", textAlign: "center", fontSize: 14.5, color: theme.palette.text.secondary }}>
            {stage === "new" ? t("home_subtitle_new") : t("home_subtitle")}
          </Typography>
        </>
      )}

      {stage !== "new" && (
        <Box sx={{ mt: "20px", display: "flex", flexDirection: "column", alignItems: "center" }}>
          <Box sx={{ width: "100%", maxWidth: 660, mb: "14px" }}>{search}</Box>
          <Box sx={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "10px" }}>
            <NewProjectButton location={{ folderId: homeFolderId }} />
            <Button
              variant="outlined"
              startIcon={<Icon iconName={uploadSource.icon} style={{ fontSize: 14 }} />}
              onClick={onAddDataset}
              sx={quickActionSx}>
              {t(uploadSource.labelKey)}
            </Button>
            <Button
              variant="outlined"
              startIcon={<Icon iconName={ICON_NAME.GLOBE} style={{ fontSize: 14 }} />}
              onClick={onBrowseCatalog}
              sx={quickActionSx}>
              {t("browse_catalog")}
            </Button>
          </Box>
        </Box>
      )}

      {showHelp && <HelpStrip mobile={mobile} />}
    </Box>
  );
};

export default HomeHero;
