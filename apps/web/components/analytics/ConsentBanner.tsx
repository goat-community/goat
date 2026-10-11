"use client";

import {
  Box,
  Button,
  Chip,
  Collapse,
  Divider,
  IconButton,
  Paper,
  Slide,
  Stack,
  Switch,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useAnalyticsConsent } from "@/hooks/useAnalyticsConsent";

interface Props {
  /** Provider key from the public-project response (e.g. "matomo"). */
  provider: string;
}

/** Provider key → human-readable name for the banner copy. */
const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
  matomo: "Matomo",
  // plausible: "Plausible",
  // ga4: "Google Analytics",
};

type BannerView = "main" | "settings";

export function ConsentBanner({ provider }: Props) {
  const theme = useTheme();
  const { decision, grant, deny } = useAnalyticsConsent();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const [view, setView] = useState<BannerView>("main");
  // Settings toggle for the (currently single) Statistik category.
  // When v2 adds more categories this becomes an object keyed by category.
  const [statistikEnabled, setStatistikEnabled] = useState(false);

  // Hidden until the visitor has made no decision yet. Returning `null`
  // (rather than display:none) ensures the banner isn't even in the DOM
  // for return visitors who've already consented or declined.
  if (decision !== null) return null;

  const providerName = PROVIDER_DISPLAY_NAMES[provider] ?? provider;

  const handleSaveSelection = () => {
    if (statistikEnabled) grant();
    else deny();
  };

  return (
    <Slide direction="up" in mountOnEnter unmountOnExit timeout={250}>
      <Paper
        elevation={12}
        role="dialog"
        aria-live="polite"
        aria-labelledby="consent-banner-title"
        sx={{
          position: "fixed",
          zIndex: theme.zIndex.snackbar,
          // Mobile: edge-to-edge bottom sheet.
          // Desktop: horizontally centred at the bottom (left/right:0 + mx:auto
          // centres a fixed-width element without using transform, which would
          // conflict with the <Slide>'s entrance animation).
          left: 0,
          right: 0,
          bottom: isMobile ? 0 : theme.spacing(2),
          mx: "auto",
          maxWidth: isMobile ? undefined : 680,
          maxHeight: isMobile ? "85vh" : undefined,
          overflowY: isMobile ? "auto" : undefined,
          p: theme.spacing(4),
          borderRadius: isMobile ? "16px 16px 0 0" : 2,
        }}>
        {view === "main" ? (
          <MainView
            providerName={providerName}
            isMobile={isMobile}
            onSettings={() => setView("settings")}
            onAccept={grant}
            onDecline={deny}
          />
        ) : (
          <SettingsView
            providerName={providerName}
            statistikEnabled={statistikEnabled}
            onToggleStatistik={setStatistikEnabled}
            isMobile={isMobile}
            onBack={() => setView("main")}
            onSave={handleSaveSelection}
            onAcceptAll={grant}
          />
        )}
      </Paper>
    </Slide>
  );
}

interface MainViewProps {
  providerName: string;
  isMobile: boolean;
  onSettings: () => void;
  onAccept: () => void;
  onDecline: () => void;
}

function MainView({
  providerName,
  isMobile,
  onSettings,
  onAccept,
  onDecline,
}: MainViewProps) {
  const theme = useTheme();
  const { t } = useTranslation("common");

  const bullets = [
    t("consent_bullet_server", "Server in Deutschland"),
    t("consent_bullet_ip", "IP-Adressen anonymisiert"),
    t("consent_bullet_no_third_party", "Keine Weitergabe an Dritte"),
    t("consent_bullet_lifetime", "Cookie-Lebensdauer: 13 Monate"),
  ];

  return (
    <Stack spacing={theme.spacing(2)}>
      <BannerHeader />

      <Typography variant="body2" color="text.secondary">
        {t(
          "consent_banner_intro",
          "Wir nutzen {{provider}}, um die Nutzung dieses Dashboards anonymisiert zu analysieren und Inhalte zu verbessern. Sie können Ihre Auswahl jederzeit ändern.",
          { provider: providerName }
        )}
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
          columnGap: theme.spacing(2),
          rowGap: theme.spacing(0.75),
        }}>
        {bullets.map((b) => (
          <Stack key={b} direction="row" alignItems="center" spacing={1}>
            <Icon
              iconName={ICON_NAME.CIRCLECHECK}
              htmlColor={theme.palette.primary.main}
              style={{ fontSize: 14, flexShrink: 0 }}
            />
            <Typography variant="caption" color="text.secondary">
              {b}
            </Typography>
          </Stack>
        ))}
      </Box>

      <Stack
        direction={isMobile ? "column" : "row"}
        spacing={1.5}
        justifyContent="flex-end"
        alignItems="stretch"
        sx={{ pt: theme.spacing(1) }}>
        <Button
          variant="text"
          color="inherit"
          onClick={onSettings}
          fullWidth={isMobile}>
          {t("consent_settings", "Einstellungen")}
        </Button>
        <Button
          variant="outlined"
          color="inherit"
          onClick={onDecline}
          fullWidth={isMobile}>
          {t("consent_decline", "Ablehnen")}
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={onAccept}
          fullWidth={isMobile}>
          {t("consent_accept", "Alle akzeptieren")}
        </Button>
      </Stack>
    </Stack>
  );
}

interface SettingsViewProps {
  providerName: string;
  statistikEnabled: boolean;
  onToggleStatistik: (v: boolean) => void;
  isMobile: boolean;
  onBack: () => void;
  onSave: () => void;
  onAcceptAll: () => void;
}

/** Cookies the Matomo tracker WILL set after consent is granted.
 * Per Matomo docs; we only inject `_pk_id` and `_pk_ses` with default
 * settings. Listed here so visitors can see exactly what they're agreeing
 * to before opting in. */
const PROVIDER_COOKIE_DETAILS: Record<
  string,
  Array<{ name: string; purposeKey: string; defaultPurpose: string; durationKey: string; defaultDuration: string }>
> = {
  matomo: [
    {
      name: "_pk_id",
      purposeKey: "consent_cookie_pk_id_purpose",
      defaultPurpose: "Anonymous visitor ID",
      durationKey: "consent_cookie_duration_13_months",
      defaultDuration: "13 months",
    },
    {
      name: "_pk_ses",
      purposeKey: "consent_cookie_pk_ses_purpose",
      defaultPurpose: "Active session",
      durationKey: "consent_cookie_duration_30_min",
      defaultDuration: "30 min",
    },
  ],
};

function SettingsView({
  providerName,
  statistikEnabled,
  onToggleStatistik,
  isMobile,
  onBack,
  onSave,
  onAcceptAll,
}: SettingsViewProps) {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Map provider key to its cookie list. Unknown provider → no details
  // section. When we add Plausible (cookieless by default), this map
  // entry will just be an empty array → the section auto-hides.
  const cookieDetails =
    PROVIDER_COOKIE_DETAILS[providerName.toLowerCase()] ?? [];

  return (
    <Stack spacing={theme.spacing(2)}>
      <Stack direction="row" alignItems="center" spacing={1}>
        <IconButton
          size="small"
          onClick={onBack}
          aria-label={t("consent_back", "Back")}>
          <Icon
            iconName={ICON_NAME.CHEVRON_LEFT}
            htmlColor={theme.palette.text.primary}
            style={{ fontSize: 16 }}
          />
        </IconButton>
        <Typography
          id="consent-banner-title"
          variant="body1"
          fontWeight="bold">
          {t("consent_banner_title", "Datenschutz & Cookies")}
        </Typography>
      </Stack>

      <Typography variant="body2" color="text.secondary">
        {t(
          "consent_banner_intro",
          "Wir nutzen {{provider}}, um die Nutzung dieses Dashboards anonymisiert zu analysieren und Inhalte zu verbessern. Sie können Ihre Auswahl jederzeit ändern.",
          { provider: providerName }
        )}
      </Typography>

      <Divider />

      <Stack direction="row" alignItems="flex-start" spacing={1.5}>
        <Box
          sx={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: 36,
            height: 36,
            borderRadius: 1,
            bgcolor: "action.hover",
            flexShrink: 0,
          }}>
          <Icon
            iconName={ICON_NAME.CHART}
            htmlColor={theme.palette.text.primary}
            style={{ fontSize: 18 }}
          />
        </Box>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Stack direction="row" alignItems="center" spacing={1} flexWrap="wrap">
            <Typography variant="body2" fontWeight="bold">
              {t("consent_category_statistik", "Statistik")} · {providerName}
            </Typography>
            <Chip
              label={t("consent_badge_anonymous", "ANONYM")}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ height: 20, fontSize: "0.625rem", fontWeight: 600 }}
            />
          </Stack>
          <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 0.5 }}>
            {t(
              "consent_category_statistik_description",
              "Hilft uns zu verstehen, welche Indikatoren am häufigsten aufgerufen werden, damit wir das Dashboard verbessern können."
            )}
          </Typography>
        </Box>
        <Switch
          checked={statistikEnabled}
          onChange={(e) => onToggleStatistik(e.target.checked)}
          color="primary"
          inputProps={{ "aria-label": t("consent_category_statistik", "Statistik") }}
        />
      </Stack>

      {cookieDetails.length > 0 && (
        <>
          <Divider />
          <Box>
            <Stack
              direction="row"
              alignItems="center"
              spacing={1}
              onClick={() => setDetailsOpen((v) => !v)}
              sx={{ cursor: "pointer", userSelect: "none" }}>
              <Icon
                iconName={ICON_NAME.CIRCLEINFO}
                htmlColor={theme.palette.text.secondary}
                style={{ fontSize: 14 }}
              />
              <Typography variant="body2" fontWeight="bold" sx={{ flex: 1 }}>
                {t("consent_cookie_details_title", "Cookie details")}
              </Typography>
              <Icon
                iconName={
                  detailsOpen ? ICON_NAME.CHEVRON_UP : ICON_NAME.CHEVRON_DOWN
                }
                htmlColor={theme.palette.text.secondary}
                style={{ fontSize: 14 }}
              />
            </Stack>
            <Collapse in={detailsOpen} unmountOnExit>
              <Stack spacing={1} sx={{ mt: 1.5 }}>
                {cookieDetails.map((c) => (
                  <Box
                    key={c.name}
                    sx={{
                      bgcolor: "action.hover",
                      borderRadius: 1,
                      px: 1.5,
                      py: 1,
                    }}>
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="baseline"
                      spacing={2}>
                      <Box sx={{ minWidth: 0, flex: 1 }}>
                        <Typography
                          variant="body2"
                          fontWeight="bold"
                          sx={{ fontFamily: "monospace" }}>
                          {c.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {t(c.purposeKey, c.defaultPurpose)}
                        </Typography>
                      </Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ flexShrink: 0 }}>
                        {t(c.durationKey, c.defaultDuration)}
                      </Typography>
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </Collapse>
          </Box>
        </>
      )}

      <Divider />

      <Stack
        direction={isMobile ? "column" : "row"}
        spacing={1.5}
        justifyContent="flex-end"
        alignItems="stretch"
        sx={{ pt: theme.spacing(1) }}>
        <Button
          variant="outlined"
          color="inherit"
          onClick={onAcceptAll}
          fullWidth={isMobile}>
          {t("consent_accept", "Alle akzeptieren")}
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={onSave}
          fullWidth={isMobile}>
          {t("consent_save_selection", "Auswahl speichern")}
        </Button>
      </Stack>
    </Stack>
  );
}

function BannerHeader() {
  const theme = useTheme();
  const { t } = useTranslation("common");
  return (
    <Stack direction="row" alignItems="center" spacing={1.5}>
      <Box
        sx={{
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          width: 36,
          height: 36,
          borderRadius: 1,
          bgcolor: "action.hover",
        }}>
        <Icon
          iconName={ICON_NAME.LOCK}
          htmlColor={theme.palette.text.primary}
          style={{ fontSize: 18 }}
        />
      </Box>
      <Typography id="consent-banner-title" variant="body1" fontWeight="bold">
        {t("consent_banner_title", "Datenschutz & Cookies")}
      </Typography>
    </Stack>
  );
}
