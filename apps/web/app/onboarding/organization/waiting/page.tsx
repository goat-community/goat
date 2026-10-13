"use client";

import LoadingButton from "@mui/lab/LoadingButton";
import { Button, Stack, Typography } from "@mui/material";
import { signOut, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";

import AuthContainer from "@p4b/ui/components/AuthContainer";
import AuthLayout from "@p4b/ui/components/AuthLayout";

import { useInvitations, useOrganization, useOrganizationCreation } from "@/lib/api/users";
import type { GetInvitationsQueryParams } from "@/lib/validations/user";

const PENDING_INVITATIONS: GetInvitationsQueryParams = { type: "organization", status: "pending" };

/**
 * Shown instead of the organization setup form to a signed-in user without an
 * organization when only administrators may create organizations. An
 * invitation that arrives in the meantime opens by itself: the lists are
 * fetched again whenever the window regains focus, or on "Check again". A
 * user who has an organization by now (an invitation accepted in another
 * tab, a bookmarked link) goes home.
 */
export default function OrganizationWaiting() {
  const { t } = useTranslation("common");
  const { status, data: session } = useSession();
  const router = useRouter();
  // Without an organization this answers 404, which is the expected case
  // here and not worth retrying.
  const {
    organization,
    mutate: mutateOrganization,
    isValidating: isOrganizationValidating,
  } = useOrganization({ shouldRetryOnError: false });
  const {
    organizationCreation,
    isError: creationError,
    mutate: mutateCreation,
    isValidating: isCreationValidating,
  } = useOrganizationCreation();
  const {
    invitations,
    mutate: mutateInvitations,
    isValidating: isInvitationsValidating,
  } = useInvitations(PENDING_INVITATIONS);
  const hasOrganization = !!organization?.id;
  const invitationId = invitations?.items?.[0]?.id;

  useEffect(() => {
    if (hasOrganization) {
      router.replace("/");
    } else if (invitationId) {
      router.replace(`/onboarding/organization/invite/${invitationId}`);
    } else if (organizationCreation?.allowed) {
      router.replace("/onboarding/organization/create");
    }
  }, [hasOrganization, invitationId, organizationCreation?.allowed, router]);

  // Also when core could not answer whether the user may create one: the
  // buttons below keep them from being stuck on an empty page.
  const waiting = organizationCreation?.allowed === false || !!creationError;

  return (
    <AuthLayout>
      <>
        {status == "authenticated" && waiting && !hasOrganization && !invitationId && (
          <AuthContainer
            headerTitle={<Typography variant="h5">{t("waiting_for_invitation")}</Typography>}
            body={
              <Stack spacing={4}>
                <Typography variant="body1">
                  {t("waiting_for_invitation_message", { email: session?.user?.email ?? "" })}
                </Typography>
                <LoadingButton
                  variant="outlined"
                  color="primary"
                  loading={isOrganizationValidating || isCreationValidating || isInvitationsValidating}
                  onClick={() => {
                    mutateOrganization();
                    mutateInvitations();
                    mutateCreation();
                  }}>
                  <Typography variant="body1" fontWeight="bold" color="inherit">
                    {t("check_again")}
                  </Typography>
                </LoadingButton>
                <Button variant="text" color="error" onClick={() => signOut({ callbackUrl: "/" })}>
                  {t("logout")}
                </Button>
              </Stack>
            }
          />
        )}
      </>
    </AuthLayout>
  );
}
