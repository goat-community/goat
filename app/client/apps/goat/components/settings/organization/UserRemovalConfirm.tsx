import React from "react";
import UserInfoModal from "./UserInfoModal";
import Modal from "@p4b/ui/components/Modal";
import { Button, Text, IconButton } from "@p4b/ui/components/theme";
import { useTheme, makeStyles } from "@/lib/theme";
import { Icon } from "@p4b/ui/components/Icon";
import { ICON_NAME } from "@p4b/ui/components/Icon";
import type { IUser } from "@/types/dashboard/organization";

interface UserRemovalFunctions {
  userInDialog: IUser | undefined;
  isModalVisible: boolean;
  removeUser: (user: IUser | undefined) => void;
  setTheUserInDialog: (user: IUser | undefined) => void;
  closeUserRemovalDialog: () => void;
  openUserRemovalDialog: (user: IUser | undefined) => void;
  editUserRole: (role: "Admin" | "User" | "Editor", user: IUser | undefined) => void;
}

interface UserRemovalConfirmProps {
  removeUserFunctions: UserRemovalFunctions;
}

const UserRemovalConfirm: React.FC<UserRemovalConfirmProps> = ({
  removeUserFunctions,
}) => {
  const {
    userInDialog,
    isModalVisible,
    removeUser,
    setTheUserInDialog,
    closeUserRemovalDialog,
    openUserRemovalDialog,
    editUserRole,
  } = removeUserFunctions;

  const theme = useTheme();
  const { classes } = useStyles();

  const renderModalHeader = () => {
    if (isModalVisible) {
      return (
        <Text className={classes.modalHeader} typo="subtitle">
          <Icon iconName={ICON_NAME.CIRCLEINFO} htmlColor={theme.colors.palette.orangeWarning.main} />{" "}
          Attention
        </Text>
      );
    } else {
      return (
        <div className={classes.modalHeader2}>
          <Text typo="subtitle" className={classes.headerText}>
            {userInDialog instanceof Object && "name" in userInDialog ? userInDialog.name : ""}
          </Text>
          <IconButton onClick={closeUserRemovalDialog} iconId="close" />
        </div>
      );
    }
  };

  return (
    <Modal
      width="523px"
      open={Boolean(userInDialog)}
      changeOpen={() => setTheUserInDialog(undefined)}
      action={
        isModalVisible ? (
          <>
            <Button onClick={closeUserRemovalDialog} variant="noBorder">
              CANCEL
            </Button>
            <Button onClick={() => removeUser(userInDialog)} variant="noBorder">
              CONFIRM
            </Button>
          </>
        ) : (
          <Button
            onClick={() => openUserRemovalDialog(userInDialog)}
            variant="noBorder"
          >
            REMOVE USER
          </Button>
        )
      }
      header={renderModalHeader()}
    >
      <UserInfoModal
        ismodalVisible={isModalVisible}
        userInDialog={userInDialog}
        editUserRole={editUserRole}
      />
    </Modal>
  );
};

const useStyles = makeStyles({ name: { UserRemovalConfirm } })((theme) => ({
  modalHeader: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
  },
  modalHeader2: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  headerText: {
    fontWeight: "normal",
  },
}));

export default UserRemovalConfirm;
