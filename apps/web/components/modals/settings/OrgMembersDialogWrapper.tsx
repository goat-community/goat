import { OrgMemberActions } from "@/types/common";
import type { MemberDialogBaseProps } from "@/types/dashboard/settings";

import DeleteMemberModal from "@/components/modals/settings/DeleteMember";

interface OrgMemberDialogProps extends Omit<MemberDialogBaseProps, "open"> {
  action: OrgMemberActions;
  onMemberDelete?: () => void;
  organizationId?: string;
}

export default function OrgMemberDialogWrapper(props: OrgMemberDialogProps) {
  const commonModalProps = {
    member: props.member,
    open: !!props.member,
    onClose: props.onClose,
  };

  return (
    <>
      {(props.action === OrgMemberActions.DELETE || props.action === OrgMemberActions.CANCEL_INVITATION) && (
        <DeleteMemberModal
          onDelete={props.onMemberDelete}
          {...commonModalProps}
          organizationId={props.organizationId}
        />
      )}
    </>
  );
}
