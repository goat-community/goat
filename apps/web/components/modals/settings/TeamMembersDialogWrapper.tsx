import { TeamMemberActions } from "@/types/common";
import type { MemberDialogBaseProps } from "@/types/dashboard/settings";

import DeleteMemberModal from "@/components/modals/settings/DeleteMember";

interface TeamMemberDialogProps extends Omit<MemberDialogBaseProps, "open"> {
  action: TeamMemberActions;
  onMemberDelete?: () => void;
  onMemberCreate?: () => void;
  teamId?: string;
}

export default function TeamMemberDialogWrapper(props: TeamMemberDialogProps) {
  const commonModalProps = {
    member: props.member,
    open: !!props.member,
    onClose: props.onClose,
  };

  return (
    <>
      {(props.action === TeamMemberActions.DELETE ||
        props.action === TeamMemberActions.CANCEL_INVITATION) && (
        <DeleteMemberModal onDelete={props.onMemberDelete} {...commonModalProps} teamId={props.teamId} />
      )}
    </>
  );
}
