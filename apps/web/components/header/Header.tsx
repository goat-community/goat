"use client";

import { Info } from "@mui/icons-material";
import { Chip, IconButton, Stack, Tooltip, Typography, useTheme } from "@mui/material";
import Divider from "@mui/material/Divider";
import { format, formatDistance, parseISO } from "date-fns";
import { Trans } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useDateFnsLocale, useTranslation } from "@/i18n/client";

import { useOrganization } from "@/lib/api/users";
import { CONTACT_US_URL, DOCS_URL, DOCS_VERSION } from "@/lib/constants";

import { useAuthZ } from "@/hooks/auth/AuthZ";

import UserInfoMenu from "@/components/UserInfoMenu";
import JobsPopper from "@/components/jobs/JobsPopper";

import { Toolbar } from "./Toolbar";

export type HeaderProps = {
  title: string;
  lastSaved?: string;
  tags?: string[];
  showHambugerMenu?: boolean;
  onMenuIconClick?: () => void;
  height?: number;
};

export default function Header(props: HeaderProps) {
  const theme = useTheme();
  const { t, i18n } = useTranslation(["common"]);
  const { tags, title, lastSaved, onMenuIconClick, showHambugerMenu, height = 52 } = props;
  const { organization } = useOrganization();
  const { isOrgAdmin } = useAuthZ();
  const dateLocale = useDateFnsLocale();
  const lng = i18n.language === "de" ? "/de" : "";
  const docsVersion = `/${DOCS_VERSION}`;
  return (
    <Toolbar
      showHambugerMenu={showHambugerMenu}
      onMenuIconClick={onMenuIconClick}
      height={height}
      LeftToolbarChild={
        <>
          <Typography variant="body1" fontWeight="bold">
            {title}
          </Typography>
          <Divider orientation="vertical" flexItem />
          {lastSaved && (
            <Typography variant="caption">
              {`${t("common:last_saved")}: ${format(parseISO(lastSaved), "hh:mma dd/MM/yyyy")
                .replace("PM", " PM")
                .replace("AM", " AM")}`}
            </Typography>
          )}
          {tags &&
            tags.map((tag) => (
              <Chip
                variant="outlined"
                label={tag}
                key={tag}
                sx={{
                  mx: theme.spacing(1),
                }}
              />
            ))}
        </>
      }
      RightToolbarChild={
        <>
          <Stack direction="row" spacing={2} justifyContent="center" alignItems="center">
            <>
              {organization && organization.on_trial && isOrgAdmin && (
                <Chip
                  icon={<Info />}
                  variant="outlined"
                  color="warning"
                  size="small"
                  label={
                    <Trans
                      i18nKey="common:your_trial_will_end_in"
                      values={{
                        expire_date: formatDistance(new Date(organization.plan_renewal_date), new Date(), {
                          locale: dateLocale,
                        }),
                      }}
                    />
                  }
                  sx={{
                    "& .MuiChip-label": {
                      fontWeight: "bold",
                      fontStyle: "normal",
                    },
                  }}
                  onClick={() => {
                    window.open(CONTACT_US_URL, "_blank");
                  }}
                />
              )}
            </>
            <Tooltip title={t("common:open_documentation")}>
              <IconButton
                size="small"
                onClick={() => {
                  window.open(`${DOCS_URL}${lng}${docsVersion}`, "_blank");
                }}>
                <Icon iconName={ICON_NAME.BOOK} fontSize="inherit" />
              </IconButton>
            </Tooltip>
            <JobsPopper />
            <Divider orientation="vertical" flexItem />
            <UserInfoMenu />
          </Stack>
        </>
      }
    />
  );
}
