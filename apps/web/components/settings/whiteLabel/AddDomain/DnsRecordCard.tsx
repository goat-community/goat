"use client";

import {
  Box,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useCustomDomainConfig } from "@/lib/api/customDomainConfig";
import { isApexDomain } from "@/lib/validations/customDomain";

interface DnsRecordCardProps {
  /** The hostname the user is configuring (e.g. "dashboards.example.com"). */
  domain: string;
}

interface CopyableCellProps {
  value: string;
}

function CopyableCell({ value }: CopyableCellProps) {
  const { t } = useTranslation("common");
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // navigator.clipboard can fail in non-secure contexts; we just no-op.
    }
  };

  return (
    <Stack direction="row" alignItems="center" spacing={1}>
      <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
        {value}
      </Typography>
      <Tooltip
        title={
          copied
            ? t("white_label_dns_copied", "Copied")
            : t("white_label_dns_copy", "Copy")
        }>
        <IconButton size="small" onClick={handleCopy} aria-label={t("copy")}>
          <Icon iconName={ICON_NAME.COPY} fontSize="small" />
        </IconButton>
      </Tooltip>
    </Stack>
  );
}

export function DnsRecordCard({ domain }: DnsRecordCardProps) {
  const { t } = useTranslation("common");
  const config = useCustomDomainConfig();
  const apex = isApexDomain(domain);
  // For subdomains, DNS providers want the relative name (just the leftmost
  // label). For apex domains, the host is "@" — a convention shared by
  // every major registrar including Namecheap.
  const host = apex ? "@" : domain.split(".")[0] || domain;

  // Apex → single A record (skip AAAA: every browser falls back to v4 fine,
  // and one record is one less thing for the customer to maintain).
  // Subdomain → single CNAME pointing at the canonical target.
  // Both forms are accepted by the reconciliation check on the backend.
  const cnameTarget = config?.cname_target ?? "";
  const apexIpv4 = config?.apex_ipv4 ?? "";
  const rows = apex
    ? [{ type: "A", host, target: apexIpv4 }]
    : [{ type: "CNAME", host, target: cnameTarget }];

  return (
    <Box
      sx={{
        border: 1,
        borderColor: "divider",
        borderRadius: 1,
        overflow: "hidden",
      }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600 }}>
              {t("white_label_dns_type", "Type")}
            </TableCell>
            <TableCell sx={{ fontWeight: 600 }}>
              {t("white_label_dns_host", "Host")}
            </TableCell>
            <TableCell sx={{ fontWeight: 600 }}>
              {t("white_label_dns_target", "Target")}
            </TableCell>
            <TableCell sx={{ fontWeight: 600 }}>
              {t("white_label_dns_ttl", "TTL")}
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.type}>
              <TableCell>
                <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                  {row.type}
                </Typography>
              </TableCell>
              <TableCell>
                <CopyableCell value={row.host} />
              </TableCell>
              <TableCell>
                <CopyableCell value={row.target} />
              </TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                  3600
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}
