"use client";

import SubscriptionCardSkeleton from "@/components/skeletons/SubscriptionCardSkeleton";
import { useInviteUserDialog, useUserRemovalDialog, useUsersData } from "@/hooks/dashboard/OrganisationHooks";
import { makeStyles, Text } from "@/lib/theme";
import { useState } from "react";

// import { Chip } from "@p4b/ui/components/DataDisplay";
import { Chip } from "@/components/common/Chip";
import { EnhancedTable } from "@p4b/ui/components/DataDisplay/EnhancedTable";
import { TextField } from "@p4b/ui/components/Inputs/TextField";
import Modal from "@p4b/ui/components/Modal";
import Banner from "@p4b/ui/components/Surfaces/Banner";
import { Card } from "@p4b/ui/components/Surfaces/Card";
import { Icon, Button, IconButton } from "@p4b/ui/components/theme";

import InviteUser from "@/components/settings/organization/InviteUser";
import UserRemovalConfirm from "@/components/settings/organization/UserRemovalConfirm";
import type { IUser } from "@/types/dashboard/organization";
import { ICON_NAME } from "@p4b/ui/components/Icon";

const ManageUsers = () => {
  const { classes } = useStyles();

  const [searchWord, setSearchWord] = useState<string>("");
  const { rawRows, setRawRows, setRows, rows, isLoading, error } = useUsersData(searchWord);
  const { isAddUser, openInviteDialog, closeInviteDialog, email, setEmail } = useInviteUserDialog();
  const { userInDialog, isModalVisible, openUserRemovalDialog, closeUserRemovalDialog, setTheUserInDialog } =
    useUserRemovalDialog();

  const columnNames = [
    {
      id: "name",
      numeric: false,
      label: "Name",
    },
    {
      id: "email",
      numeric: false,
      label: "E-mail",
    },
    {
      id: "role",
      numeric: false,
      label: "Role",
    },
    {
      id: "status",
      numeric: false,
      label: "Status",
    },
    {
      id: "added",
      numeric: false,
      label: "Added",
    },
  ];

  // Functions

  function sendInvitation() {
    const newUserInvite: IUser = {
      name: "Luca William Silva",
      email,
      role: "Admin",
      status: "Invite sent",
      Added: "23 Jun 19",
    };
    setRawRows([...rawRows, newUserInvite]);
    closeInviteDialog();
  }

  function editUserRole(role: "Admin" | "User" | "Editor", user: IUser | undefined) {
    if (user) {
      const modifiedUsers = rows.map((row: IUser) => (row.email === user.email ? { ...row, role } : row));
      setRows(modifiedUsers);
    }
  }

  function removeUser(user: IUser | undefined) {
    if (user) {
      const modifiedUsers = rows.filter((row: IUser) => row.email !== user.email);
      setRawRows(modifiedUsers);
      closeUserRemovalDialog();
    }
  }

  function getStatus() {
    if (isLoading) {
      return <SubscriptionCardSkeleton />;
    } else if (error) {
      return "There is an error with the connection, make sure to be connected to a valid network!";
    } else {
      return "No Result";
    }
  }

  function returnRightFormat(users) {
    return users.map((user) => {
      const modifiedVisualData = user;
      const label =
        typeof user.status !== "string" && user.status?.props ? user.status.props.label : user.status;
      let color: "dark" | "focus" | "orangeWarning" | "redError" | undefined;
      let icon: ICON_NAME | undefined;

      switch (label) {
        case "Active":
          color = "focus";
          icon = ICON_NAME.CIRCLECHECK;
          break;
        case "Invite sent":
          color = "dark";
          icon = ICON_NAME.EMAIL;
          break;
        case "Expired":
          color = "orangeWarning";
          icon = ICON_NAME.CIRCLEINFO;
          break;
      }

      modifiedVisualData.status = (
        <Chip className={classes.chip} label={label} variant="Border" color={color} icon={icon} />
      );
      return modifiedVisualData;
    });
  }

  return (
    <div>
      <div className={classes.container}>
        <div className={classes.head}>
          <Icon
            iconId="user"
            wrapped="circle"
            bgVariant="gray2"
            bgOpacity={0.6}
            iconVariant="secondary"
            size="medium"
          />
          <Text typo="body 1" className={classes.name}>
            Organization name
          </Text>
        </div>
        <div className={classes.search}>
          <TextField
            className={classes.searchInput}
            type="text"
            label="Search"
            size="small"
            onValueBeingTypedChange={({ value }) => setSearchWord(value)}
          />
          <Icon iconId="filter" size="medium" iconVariant="gray" />
          <div style={{ position: "relative" }}>
            <Button onClick={openInviteDialog} className={classes.searchButton}>
              Invite user
            </Button>
            {/* Invite User Dialog */}
            {isAddUser ? (
              <Modal
                width="444px"
                open={isAddUser}
                changeOpen={closeInviteDialog}
                action={
                  <>
                    <Button variant="noBorder" onClick={closeInviteDialog}>
                      CANCEL
                    </Button>
                    <Button variant="noBorder" onClick={sendInvitation}>
                      SEND INVITATION
                    </Button>
                  </>
                }
                header={
                  <div className={classes.modalHeader2}>
                    <Text typo="subtitle" className={classes.headerText}>
                      Invite user
                    </Text>
                    <IconButton onClick={closeInviteDialog} iconId="close" />
                  </div>
                }>
                <InviteUser setEmail={setEmail} />
              </Modal>
            ) : null}
          </div>
        </div>
      </div>
      <Card noHover={true} className={classes.tableCard}>
        {/* ManageUsers Table */}
        {rows.length ? (
          <EnhancedTable
            rows={returnRightFormat([...rows])}
            columnNames={columnNames}
            openDialog={(value: object | null) => (value ? setTheUserInDialog(value as IUser) : undefined)}
            action={<IconButton type="submit" iconId="moreVert" size="medium" />}
            dense={false}
            alternativeColors={true}
          />
        ) : (
          <Text typo="body 1" color="secondary">
            {getStatus()}
          </Text>
        )}
      </Card>
      <Banner
        actions={<Button>Subscribe Now</Button>}
        content={
          <Text className={classes.bannerText} typo="body 1">
            Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
            massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.{" "}
          </Text>
        }
        image="https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4"
        imageSide="right"
      />
      {/* Confirm User Removal */}
      <UserRemovalConfirm
        removeUserFunctions={{
          userInDialog: userInDialog ? userInDialog : undefined,
          isModalVisible,
          removeUser,
          setTheUserInDialog,
          closeUserRemovalDialog,
          openUserRemovalDialog,
          editUserRole,
        }}
      />
    </div>
  );
};

const useStyles = makeStyles({ name: { ManageUsers } })((theme) => ({
  bannerText: {
    color: "white",
    "@media (max-width: 1268px)": {
      fontSize: "14px",
    },
  },
  name: {
    fontWeight: "bold",
  },
  head: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  search: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: theme.spacing(4),
    marginBottom: theme.spacing(3),
  },
  searchButton: {
    width: "131px",
  },
  container: {
    padding: `0px ${theme.spacing(3)}px`,
    marginBottom: theme.spacing(2),
  },
  searchInput: {
    flexGrow: "1",
  },
  tableCard: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(5),
  },
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
  chip: {
    "& .mui-6od3lo-MuiChip-label": {
      padding: "4px",
    },
  },
  headerText: {
    fontWeight: "normal",
  },
}));

export default ManageUsers;
