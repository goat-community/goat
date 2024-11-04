import { useMemo } from "react";

import { useOrganization, useUserProfile } from "@/lib/api/users";
import type { FeatureName } from "@/lib/validations/organization";
import { featureToPlanMap, organizationRoles } from "@/lib/validations/organization";
import { type Team, teamRoles } from "@/lib/validations/team";

interface Options {
  team?: Team;
}

export function useAuthZ(options: Options = {}) {
  const { userProfile, isLoading: isUserProfileLoading } = useUserProfile();
  const { organization } = useOrganization();
  const roles = userProfile?.roles;

  const isOrgAdmin = useMemo(() => {
    if (!roles) return false;
    return roles.includes(organizationRoles.OWNER) || roles.includes(organizationRoles.ADMIN);
  }, [roles]);

  const isOrgEditor = useMemo(() => {
    if (!roles) return false;
    return roles.includes(organizationRoles.EDITOR) || isOrgAdmin;
  }, [roles, isOrgAdmin]);

  const isTeamOwner = useMemo(() => {
    const { team } = options;
    if (!team || !roles) return false;
    return team.role === teamRoles.OWNER;
  }, [roles, options]);

  const isProjectEditor = useMemo(() => {
    return isOrgEditor;
  }, [isOrgEditor]);

  const isLoading = useMemo(() => {
    return isUserProfileLoading;
  }, [isUserProfileLoading]);

  const isAppFeatureEnabled = (feature: FeatureName) => {
    const organizationPlan = organization?.plan_name;
    const plansEnabled = featureToPlanMap[feature];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (organizationPlan && plansEnabled && plansEnabled.includes(organizationPlan as any)) {
      return true;
    }

    return false;
  }

  return {
    isLoading,
    isOrgAdmin,
    isOrgEditor,
    isTeamOwner,
    isProjectEditor,
    isAppFeatureEnabled,
  };
}
