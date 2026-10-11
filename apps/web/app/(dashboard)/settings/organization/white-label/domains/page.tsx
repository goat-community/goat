"use client";

import {
  Alert,
  Box,
  Button,
  Divider,
  Skeleton,
  Stack,
  Typography,
  useTheme,
} from "@mui/material";
import { useState } from "react";
import { Trans, useTranslation } from "react-i18next";
import { toast } from "react-toastify";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import {
  deleteCustomDomain,
  recheckCustomDomain,
  unassignDomainFromProject,
  useOrganizationDomains,
} from "@/lib/api/customDomains";
import { useCustomDomainConfig } from "@/lib/api/customDomainConfig";
import { useOrganization } from "@/lib/api/users";
import type { CustomDomain } from "@/lib/validations/customDomain";

import { AddDomainDialog } from "@/components/settings/whiteLabel/AddDomainDialog";
import { DeleteDomainDialog } from "@/components/settings/whiteLabel/DeleteDomainDialog";
import { DomainDetailDrawer } from "@/components/settings/whiteLabel/DomainDetailDrawer";
import { DomainList } from "@/components/settings/whiteLabel/DomainList";

export default function WhiteLabelDomainsPage() {
  const theme = useTheme();
  const { t } = useTranslation("common");
  const { organization, isLoading: isOrgLoading } = useOrganization();
  const orgId = organization?.id;
  const { domains, isLoading, mutate } = useOrganizationDomains(orgId);
  const customDomainConfig = useCustomDomainConfig();

  const [addOpen, setAddOpen] = useState(false);
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);
  const [domainToDelete, setDomainToDelete] = useState<CustomDomain | null>(null);

  const handleRecheck = async (domain: CustomDomain) => {
    if (!orgId) return;
    try {
      await recheckCustomDomain(orgId, domain.id);
      await mutate();
      toast.success(
        t("white_label_custom_domains_recheck_success", "Recheck triggered")
      );
    } catch {
      toast.error(t("white_label_custom_domains_recheck_error", "Recheck failed"));
    }
  };

  const handleConfirmDelete = async () => {
    if (!orgId || !domainToDelete) return;
    try {
      await deleteCustomDomain(orgId, domainToDelete.id);
      await mutate();
      setDomainToDelete(null);
      // Also close the detail drawer if it points at the same domain.
      if (selectedDomainId === domainToDelete.id) {
        setSelectedDomainId(null);
      }
      toast.success(
        t("white_label_custom_domains_delete_success", "Domain deleted")
      );
    } catch {
      toast.error(t("white_label_custom_domains_delete_error", "Delete failed"));
    }
  };

  const handleUnassign = async (domain: CustomDomain) => {
    if (!domain.assigned_project_id) return;
    try {
      await unassignDomainFromProject(domain.assigned_project_id);
      await mutate();
      toast.success(
        t("white_label_custom_domains_unassign_success", "Domain unassigned")
      );
    } catch {
      toast.error(t("white_label_custom_domains_unassign_error", "Unassign failed"));
    }
  };

  const isBusy = isOrgLoading || (isLoading && !domains);

  return (
    <Box sx={{ p: 4 }}>
      <Stack spacing={theme.spacing(6)}>
        <Divider />
        <Stack
          direction="row"
          alignItems="flex-start"
          justifyContent="space-between"
          spacing={2}>
          <Box>
            <Typography variant="body1" fontWeight="bold">
              {t("white_label_custom_domains_title", "Custom Domains")}
            </Typography>
            <Typography variant="caption">
              {t(
                "white_label_custom_domains_description",
                "Publish your dashboards on your own domain. Each domain serves one published project."
              )}
            </Typography>
          </Box>
          {orgId && domains && domains.length > 0 && (
            <Button
              variant="contained"
              sx={{ whiteSpace: "nowrap" }}
              startIcon={<Icon fontSize="small" iconName={ICON_NAME.PLUS} />}
              onClick={() => setAddOpen(true)}
              aria-label={t("white_label_add_domain_title", "Add custom domain")}
              name="add-custom-domain">
              {t("white_label_add_domain_title", "Add custom domain")}
            </Button>
          )}
        </Stack>
        <Divider />

        <Alert severity="info" icon={<Icon iconName={ICON_NAME.INFO} fontSize="small" />}>
          <Trans
            i18nKey="common:white_label_custom_domains_dns_banner_subdomain"
            defaults="Subdomain (e.g. <code>maps.example.com</code>): create a CNAME record pointing at <code>{{target}}</code>."
            values={{ target: customDomainConfig?.cname_target ?? "" }}
            components={{ code: <code style={{ fontFamily: "monospace" }} /> }}
          />
          <br />
          <Trans
            i18nKey="common:white_label_custom_domains_dns_banner_apex"
            defaults="Apex (e.g. <code>example.com</code>): create an A record pointing at <code>{{ip}}</code>."
            values={{ ip: customDomainConfig?.apex_ipv4 ?? "" }}
            components={{ code: <code style={{ fontFamily: "monospace" }} /> }}
          />
        </Alert>

        {isBusy && (
          <Stack spacing={2}>
            <Skeleton variant="rectangular" height={48} />
            <Skeleton variant="rectangular" height={48} />
            <Skeleton variant="rectangular" height={48} />
          </Stack>
        )}

        {!isBusy && domains && domains.length === 0 && (
          <Box
            sx={{
              border: 1,
              borderColor: "divider",
              borderRadius: 1,
              p: 6,
              textAlign: "center",
            }}>
            <Typography variant="body1" fontWeight="bold" sx={{ mb: 1 }}>
              {t(
                "white_label_custom_domains_empty_title",
                "No custom domains registered"
              )}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 3, maxWidth: 480, mx: "auto" }}>
              {t(
                "white_label_custom_domains_empty_description",
                "Add a domain to publish dashboards under your organization's URL. You'll need access to the domain's DNS records."
              )}
            </Typography>
            <Button
              variant="contained"
              startIcon={<Icon fontSize="small" iconName={ICON_NAME.PLUS} />}
              onClick={() => setAddOpen(true)}
              disabled={!orgId}>
              {t(
                "white_label_custom_domains_add_first",
                "Add your first domain"
              )}
            </Button>
          </Box>
        )}

        {!isBusy && domains && domains.length > 0 && (
          <DomainList
            domains={domains}
            assignedProjectNames={Object.fromEntries(
              domains
                .filter((d) => d.assigned_project_name)
                .map((d) => [d.id, d.assigned_project_name as string])
            )}
            onOpenDetail={(d) => setSelectedDomainId(d.id)}
            onRecheck={handleRecheck}
            onDelete={(d) => setDomainToDelete(d)}
            onUnassign={handleUnassign}
          />
        )}
      </Stack>

      {orgId && (
        <AddDomainDialog
          open={addOpen}
          onClose={() => setAddOpen(false)}
          organizationId={orgId}
          onCreated={() => {
            mutate();
          }}
        />
      )}

      {orgId && (
        <DomainDetailDrawer
          open={selectedDomainId !== null}
          onClose={() => setSelectedDomainId(null)}
          organizationId={orgId}
          domainId={selectedDomainId}
          onDelete={(d) => setDomainToDelete(d)}
        />
      )}

      <DeleteDomainDialog
        open={domainToDelete !== null}
        onClose={() => setDomainToDelete(null)}
        domain={domainToDelete}
        onConfirm={handleConfirmDelete}
      />
    </Box>
  );
}
