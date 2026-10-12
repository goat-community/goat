"use client";

import { Box, Button, Typography, alpha, useTheme } from "@mui/material";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { addLayerSource } from "@/components/addLayer/sources";
import SurfaceCard from "@/components/dashboard/common/SurfaceCard";
import HomeSection from "@/components/dashboard/home/HomeSection";

// The Upload dataset quick action, labelled and drawn as in the Add layer menu.
const uploadSource = addLayerSource("upload");

interface DataWaysProps {
  onUpload: () => void;
  onCatalog: () => void;
}

/**
 * H9/§3's "Get some data in" band: two ways into a first dataset — the
 * catalog (tinted, since it needs no preparation) and an upload of the
 * caller's own files (plain). Shown on Home only in the New stage, while no
 * dataset is reachable yet.
 */
const DataWays = ({ onUpload, onCatalog }: DataWaysProps) => {
  const { t } = useTranslation("common");
  const theme = useTheme();

  return (
    <HomeSection title={t("get_some_data_in")}>
      <Box sx={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
        <SurfaceCard
          sx={{
            flex: 1,
            minWidth: 240,
            p: "20px",
            backgroundColor: alpha(theme.palette.primary.main, 0.12),
            borderColor: alpha(theme.palette.primary.main, 0.24),
          }}>
          <Icon iconName={ICON_NAME.GLOBE} style={{ fontSize: 22, color: theme.palette.primary.main }} />
          <Typography sx={{ fontSize: 15, fontWeight: 700, mt: "10px" }}>
            {t("data_way_catalog_title")}
          </Typography>
          <Typography sx={{ fontSize: 13.5, color: theme.palette.text.secondary, mt: "4px" }}>
            {t("data_way_catalog_body")}
          </Typography>
          <Button
            variant="contained"
            onClick={onCatalog}
            sx={{ mt: "16px", borderRadius: "999px", textTransform: "none", fontWeight: 600 }}>
            {t("browse_catalog")}
          </Button>
        </SurfaceCard>

        <SurfaceCard sx={{ flex: 1, minWidth: 240, p: "20px" }}>
          <Icon iconName={uploadSource.icon} style={{ fontSize: 22, color: theme.palette.primary.main }} />
          <Typography sx={{ fontSize: 15, fontWeight: 700, mt: "10px" }}>
            {t("data_way_upload_title")}
          </Typography>
          <Typography sx={{ fontSize: 13.5, color: theme.palette.text.secondary, mt: "4px" }}>
            {t("data_way_upload_body")}
          </Typography>
          <Button
            variant="outlined"
            onClick={onUpload}
            sx={{ mt: "16px", borderRadius: "999px", textTransform: "none", fontWeight: 600 }}>
            {t(uploadSource.labelKey)}
          </Button>
        </SurfaceCard>
      </Box>
    </HomeSection>
  );
};

export default DataWays;
