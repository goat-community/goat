import type { OrganizationMember } from "@/lib/validations/organization";
import type { TeamMember } from "@/lib/validations/team";

import type { DialogBaseProps } from "@/types/common/dialog";

export interface MemberDialogBaseProps extends DialogBaseProps {
  open: boolean;
  onClose?: () => void;
  member: OrganizationMember | TeamMember;
}

