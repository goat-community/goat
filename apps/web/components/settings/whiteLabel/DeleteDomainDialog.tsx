"use client";

import { Alert, Box, Typography } from "@mui/material";
import { useState } from "react";
import { Trans, useTranslation } from "react-i18next";
import { toast } from "react-toastify";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import type { CustomDomain } from "@/lib/validations/customDomain";

import AppDialog, { AppDialogFooter } from "@/components/common/AppDialog";

interface DeleteDomainDialogProps {
  open: boolean;
  onClose: () => void;
  domain: CustomDomain | null;
  /** Pass a project name when the domain is currently assigned. Triggers the heavier copy. */
  assignedProjectName?: string;
  onConfirm: () => Promise<void>;
}

export function DeleteDomainDialog({
  open,
  onClose,
  domain,
  assignedProjectName,
  onConfirm,
}: DeleteDomainDialogProps) {
  const { t } = useTranslation("common");
  const [isBusy, setIsBusy] = useState(false);

  const isAssigned = Boolean(assignedProjectName);

  const handleConfirm = async () => {
    setIsBusy(true);
    try {
      await onConfirm();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : t("white_label_delete_failed", "Failed to delete domain");
      toast.error(message);
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <AppDialog
      open={open}
      onClose={onClose}
      icon={ICON_NAME.TRASH}
      tone="warning"
      title={t("white_label_delete_title", "Delete custom domain")}
      maxWidth={600}
      closeDisabled={isBusy}
      footer={
        <AppDialogFooter
          onCancel={onClose}
          cancelDisabled={isBusy}
          primaryLabel={
            isAssigned
              ? t("white_label_delete_confirm_assigned", "Delete domain")
              : t("white_label_delete_confirm_unassigned", "Delete")
          }
          onPrimary={() => void handleConfirm()}
          primaryColor="error"
          primaryLoading={isBusy}
        />
      }>
      {domain && (
        <Box sx={{ pt: 1 }}>
          <Typography variant="body2" sx={{ mb: 2 }}>
            <Trans
              i18nKey="common:white_label_delete_identify"
              defaults="You are about to delete <b>{{domain}}</b>."
              values={{ domain: domain.base_domain }}
              components={{ b: <b /> }}
            />
          </Typography>

          {isAssigned ? (
            <>
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Trans
                  i18nKey="common:white_label_delete_assigned_warning"
                  defaults="This domain is currently assigned to <b>{{project}}</b>. Deleting it will immediately stop serving the dashboard at this URL."
                  values={{ project: assignedProjectName ?? "" }}
                  components={{ b: <b /> }}
                />
              </Alert>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {t("white_label_delete_consequences_intro", "This action will:")}
              </Typography>
              <Box component="ul" sx={{ pl: 3, m: 0 }}>
                <li>
                  <Typography variant="body2" color="text.secondary">
                    {t("white_label_delete_consequence_unassign", "Unassign the domain from the project")}
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" color="text.secondary">
                    {t("white_label_delete_consequence_cert", "Remove the SSL certificate")}
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" color="text.secondary">
                    {t("white_label_delete_consequence_serve", "Stop serving the dashboard at this URL")}
                  </Typography>
                </li>
              </Box>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary">
              {t(
                "white_label_delete_unassigned_description",
                "This domain is not assigned to any project. Removing it will free the certificate slot."
              )}
            </Typography>
          )}
        </Box>
      )}
    </AppDialog>
  );
}
