import { Avatar, Badge, Box, Divider, IconButton, Typography, useTheme } from "@mui/material";
import { signOut } from "next-auth/react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useOrganization, useUserProfile } from "@/lib/api/users";
import { AUTH_DISABLED } from "@/lib/constants";

import { ArrowPopper } from "@/components/ArrowPoper";
import { HeaderPopoverHeader, HeaderPopoverList, HeaderPopoverRow } from "@/components/header/HeaderPopover";
import HeaderPopoverPaper, { HEADER_POPOVER_PLACEMENT } from "@/components/header/HeaderPopoverPaper";
import { SupportMenuEntries, supportCountLabel, useSupportCounts } from "@/components/support/SupportMenu";

export default function UserInfoMenu({ withSupport = false }: { withSupport?: boolean }) {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const [open, setOpen] = useState(false);
  const { organization } = useOrganization();
  const { userProfile } = useUserProfile();
  // On a phone the header has no room for the support icon, so its entries (and its badge) move in here.
  const supportCounts = useSupportCounts(withSupport);
  const needsReply = supportCounts?.needsReply ?? 0;
  const unread = supportCounts?.unread ?? 0;
  const countLabel = supportCounts ? supportCountLabel(t, supportCounts) : undefined;
  return (
    <>
      <ArrowPopper
        content={
          <HeaderPopoverPaper>
            <HeaderPopoverHeader
              title={organization?.name ?? t("organization")}
              leading={
                organization?.avatar ? (
                  <Avatar
                    sx={{ width: 28, height: 28 }}
                    alt={organization.name || t("organization")}
                    src={organization.avatar}
                  />
                ) : (
                  <Avatar sx={{ width: 28, height: 28, bgcolor: "rgba(71, 219, 153, 0.12)" }}>
                    <Icon
                      iconName={ICON_NAME.ORGANIZATION}
                      htmlColor={theme.palette.primary.main}
                      style={{ fontSize: 14 }}
                    />
                  </Avatar>
                )
              }>
              {userProfile && (
                <Box sx={{ mt: "10px" }}>
                  <Typography sx={{ fontSize: 13.5, fontWeight: 600 }}>
                    {userProfile.firstname} {userProfile.lastname}
                  </Typography>
                  <Typography sx={{ fontSize: 11.5, color: theme.palette.text.secondary }}>
                    {userProfile.roles?.length > 0
                      ? userProfile.roles.map((role) => t(role)).join(", ")
                      : t("user")}
                  </Typography>
                </Box>
              )}
            </HeaderPopoverHeader>
            {(withSupport || !AUTH_DISABLED) && (
              <HeaderPopoverList>
                {withSupport && (
                  <SupportMenuEntries counts={supportCounts} onNavigate={() => setOpen(false)} />
                )}
                {withSupport && !AUTH_DISABLED && <Divider sx={{ my: "4px" }} />}
                {!AUTH_DISABLED && (
                  <HeaderPopoverRow
                    tone="danger"
                    icon={ICON_NAME.SIGNOUT}
                    label={t("logout")}
                    onClick={() => signOut({ callbackUrl: process.env.NEXT_PUBLIC_APP_URL })}
                  />
                )}
              </HeaderPopoverList>
            )}
          </HeaderPopoverPaper>
        }
        open={open}
        placement={HEADER_POPOVER_PLACEMENT}
        arrow={false}
        onClose={() => setOpen(false)}>
        <IconButton
          onClick={() => {
            setOpen(!open);
          }}
          size="small"
          aria-label={countLabel ? `${t("account_menu")}: ${countLabel}` : t("account_menu")}
          aria-expanded={open}>
          <Badge
            variant="dot"
            color={needsReply ? "warning" : "primary"}
            invisible={!needsReply && !unread}
            overlap="circular"
            sx={{
              "& .MuiBadge-dot": {
                width: 10,
                height: 10,
                borderRadius: "50%",
                border: `2px solid ${theme.palette.background.paper}`,
              },
            }}>
            {userProfile?.avatar ? (
              <Avatar
                sx={{ width: 36, height: 36 }}
                alt={userProfile.email || t("user")}
                src={userProfile?.avatar}
              />
            ) : (
              <Avatar sx={{ width: 36, height: 36 }} alt={userProfile?.email || t("user")}>
                <Icon fontSize="inherit" iconName={ICON_NAME.USER} htmlColor="inherit" />
              </Avatar>
            )}
          </Badge>
        </IconButton>
      </ArrowPopper>
    </>
  );
}
