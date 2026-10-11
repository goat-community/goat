"use client";

import { LoadingButton } from "@mui/lab";
import {
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";
import dayjs from "dayjs";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { recheckCustomDomain, useOrganizationDomain } from "@/lib/api/customDomains";
import type { CustomDomain } from "@/lib/validations/customDomain";

import { DnsRecordCard } from "./AddDomain/DnsRecordCard";
import { DomainStatusChip } from "./DomainStatusChip";

interface DomainDetailDrawerProps {
  open: boolean;
  onClose: () => void;
  organizationId: string;
  /** null when no domain is selected; SWR is a no-op in that case. */
  domainId: string | null;
  onDelete: (domain: CustomDomain) => void;
}

function formatTimestamp(iso: string | null): string | null {
  if (!iso) return null;
  return dayjs(iso).format("YYYY-MM-DD HH:mm");
}

export function DomainDetailDrawer({
  open,
  onClose,
  organizationId,
  domainId,
  onDelete,
}: DomainDetailDrawerProps) {
  const { t } = useTranslation("common");
  const [isRechecking, setIsRechecking] = useState(false);

  // Polling key collapses to null when the drawer is closed or no domain is
  // selected, so SWR stops fetching automatically.
  const { domain, isLoading } = useOrganizationDomain(
    open && domainId ? organizationId : undefined,
    open && domainId ? domainId : undefined,
    { polling: open }
  );

  const handleRecheck = async () => {
    if (!domain) return;
    setIsRechecking(true);
    try {
      await recheckCustomDomain(organizationId, domain.id);
    } catch {
      toast.error(t("white_label_detail_recheck_failed", "Failed to recheck DNS"));
    } finally {
      setIsRechecking(false);
    }
  };

  const showDnsCard =
    domain && (domain.dns_status === "pending" || domain.dns_status === "failed");

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{ sx: { width: 480, maxWidth: "100%" } }}>
      <Box sx={{ p: 3, height: "100%", display: "flex", flexDirection: "column" }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
          <Typography variant="h6">
            {t("white_label_detail_title", "Domain details")}
          </Typography>
          <IconButton onClick={onClose} aria-label={t("close")}>
            <Icon iconName={ICON_NAME.CLOSE} fontSize="small" />
          </IconButton>
        </Stack>

        {isLoading && !domain && (
          <Stack spacing={2}>
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="rectangular" height={32} />
            <Skeleton variant="rectangular" height={120} />
          </Stack>
        )}

        {domain && (
          <Stack spacing={3} sx={{ flex: 1, overflow: "auto" }}>
            <Box>
              <Typography variant="body1" sx={{ fontFamily: "monospace", fontWeight: 600 }}>
                {domain.base_domain}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t("white_label_detail_added_at", "Added {{date}}", {
                  date: dayjs(domain.created_at).format("YYYY-MM-DD"),
                })}
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 1 }}>
                {t("white_label_detail_status", "Status")}
              </Typography>
              <DomainStatusChip domain={domain} />
            </Box>

            {showDnsCard && (
              <Box>
                <Typography variant="body2" fontWeight={600} sx={{ mb: 1 }}>
                  {t("white_label_detail_required_dns", "Required DNS record")}
                </Typography>
                <DnsRecordCard domain={domain.base_domain} />
              </Box>
            )}

            {(domain.dns_status_message || domain.cert_status_message) && (
              <Box>
                <Typography variant="body2" fontWeight={600} sx={{ mb: 1 }}>
                  {t("white_label_detail_what_we_found", "What we found")}
                </Typography>
                <Stack spacing={1}>
                  {domain.dns_status_message && (
                    <Typography variant="body2" color="text.secondary">
                      {t("white_label_detail_dns_label", "DNS")}: {domain.dns_status_message}
                    </Typography>
                  )}
                  {domain.cert_status_message && (
                    <Typography variant="body2" color="text.secondary">
                      {t("white_label_detail_cert_label", "Certificate")}:{" "}
                      {domain.cert_status_message}
                    </Typography>
                  )}
                </Stack>
              </Box>
            )}

            {domain.dns_last_checked_at && (
              <Typography variant="caption" color="text.secondary">
                {t("white_label_detail_last_checked", "Last checked {{when}}", {
                  when: formatTimestamp(domain.dns_last_checked_at),
                })}
              </Typography>
            )}
          </Stack>
        )}

        {domain && (
          <>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={1} justifyContent="flex-end">
              <LoadingButton
                variant="text"
                loading={isRechecking}
                onClick={handleRecheck}>
                <Typography variant="body2" fontWeight="bold">
                  {t("white_label_detail_recheck_now", "Recheck now")}
                </Typography>
              </LoadingButton>
              <Button
                variant="outlined"
                color="error"
                onClick={() => onDelete(domain)}>
                <Typography variant="body2" fontWeight="bold" color="inherit">
                  {t("white_label_detail_delete_domain", "Delete domain")}
                </Typography>
              </Button>
            </Stack>
          </>
        )}
      </Box>
    </Drawer>
  );
}
