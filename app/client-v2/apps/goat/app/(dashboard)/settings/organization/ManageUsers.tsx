"use client";

import { makeStyles } from "@/lib/theme";
import { Text } from "@/lib/theme";
import { useState } from "react";

import Banner from "@p4b/ui/components/Banner";
import { Card } from "@p4b/ui/components/Card";
import Dialog from "@p4b/ui/components/Dialog";
import EnhancedTable from "@p4b/ui/components/EnhancedTable";
import Modal from "@p4b/ui/components/Modal";
import { SelectField } from "@p4b/ui/components/SelectField";
import Table from "@p4b/ui/components/Table";
import { TextField } from "@p4b/ui/components/Text/TextField";
import { Icon, Button } from "@p4b/ui/components/theme";

interface RowsType {
  name: string;
  email: string;
  role: string;
  status: React.ReactNode;
  Added: string;
}

const ManageUsers = () => {
  const { classes } = useStyles();
  const [userInDialog, setUserInDialog] = useState<RowsType | null>();
  const [addUserDialog, setAddUserDialog] = useState(false);
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [ismodalVisible, setModalVisible] = useState<boolean>(false);
  // const open = Boolean(anchorEl);
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

  const extensionColumns = ["Extensions", "Study Area"];
  const extensionRows: { extension: string; studyarea: string }[] = [
    {
      extension: "Active mobility",
      studyarea: "Greater Munich",
    },
    {
      extension: "Motorised mobility",
      studyarea: "Greater Munich",
    },
  ];

  const rows: RowsType[] = [
    {
      name: "Luca William Silva",
      email: "john.wloremipsum@gmail.com",
      role: "Admin",
      status: (
        <Button startIcon="check" className={classes.buttonSmall}>
          Active
        </Button>
      ),
      Added: "23 Jun 19",
    },
    {
      name: "Fenix William Silva",
      email: "john.wloremipsum@gmail.com",
      role: "Admin",
      status: (
        <Button variant="secondary" startIcon="email" className={classes.buttonSmall}>
          Invite sent
        </Button>
      ),
      Added: "23 Jun 19",
    },
    {
      name: "Adam William Silva",
      email: "john.wloremipsum@gmail.com",
      role: "Admin",
      status: (
        <Button variant="warning" startIcon="warnOutlined" className={classes.buttonSmall}>
          Expired
        </Button>
      ),
      Added: "23 Jun 19",
    },
    {
      name: "John William Silva",
      email: "john.wloremipsum@gmail.com",
      role: "Admin",
      status: (
        <Button startIcon="check" className={classes.buttonSmall}>
          Active
        </Button>
      ),
      Added: "23 Jun 19",
    },
    {
      name: "John William Silva",
      email: "john.wloremipsum@gmail.com",
      role: "Admin",
      status: (
        <Button variant="secondary" startIcon="email" className={classes.buttonSmall}>
          Invite sent
        </Button>
      ),
      Added: "23 Jun 19",
    },
    {
      name: "John William Silva",
      email: "john.wloremipsum@gmail.com",
      role: "Admin",
      status: (
        <Button variant="secondary" startIcon="email" className={classes.buttonSmall}>
          Invite sent
        </Button>
      ),
      Added: "23 Jun 19",
    },
  ];

  function openAddUserDialog(event: React.MouseEvent<HTMLButtonElement>) {
    setAnchorEl(event.currentTarget);
    setAddUserDialog(true);
  }

  function handleAddUserClose() {
    setAnchorEl(null);
    setAddUserDialog(false);
  }

  function openModal() {
    setModalVisible(true);
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
          <TextField className={classes.searchInput} type="text" label="Search" size="small" />
          <Icon iconId="filter" size="medium" iconVariant="gray" />
          <div style={{ position: "relative" }}>
            <Button onClick={openAddUserDialog} className={classes.searchButton}>
              Invite user
            </Button>
            {addUserDialog ? (
              <Dialog
                title="Invite team mate"
                width="444px"
                direction="right"
                anchorEl={anchorEl}
                action={
                  <div className={classes.buttons}>
                    <Button variant="noBorder" onClick={handleAddUserClose}>
                      CANCEL
                    </Button>
                    <Button variant="noBorder">SEND INVITATION</Button>
                  </div>
                }
                onClick={handleAddUserClose}>
                <div className={classes.head}>
                  <Icon
                    iconId="user"
                    wrapped="circle"
                    bgVariant="gray2"
                    bgOpacity={0.6}
                    iconVariant="secondary"
                    size="small"
                  />
                  <Text typo="body 1">Organization name</Text>
                </div>
                <Text typo="body 3">
                  Send an invitation via email <br /> The receiver will get a link with 72 hours of expiration
                </Text>
                <div className={classes.formInputs}>
                  <TextField size="small" type="email" label="Email address" />
                  <SelectField
                    size="small"
                    defaultValue="editor"
                    label="Permission"
                    options={[
                      {
                        name: "Editor",
                        value: "editor",
                      },
                      {
                        name: "Admin",
                        value: "admin",
                      },
                      {
                        name: "Guest",
                        value: "guest",
                      },
                    ]}
                  />
                </div>
              </Dialog>
            ) : null}
          </div>
        </div>
      </div>
      <Card noHover={true} className={classes.tableCard}>
        <EnhancedTable
          rows={rows}
          columnNames={columnNames}
          openDialog={setUserInDialog}
          dialog={{
            title: userInDialog ? userInDialog.name : "unknown",
            action: (
              <div style={{ textAlign: "right" }}>
                <Button onClick={openModal} variant="noBorder">
                  REMOVE USER
                </Button>
              </div>
            ),
            body: (
              <div>
                <div className={classes.userDataContainer}>
                  <span className={classes.userDataText}>
                    <Text typo="body 2" className={classes.userDataTitle}>
                      Name:{" "}
                    </Text>{" "}
                    <Text typo="label 2">{userInDialog ? userInDialog?.name : ""}</Text>
                  </span>
                  <span className={classes.userDataText}>
                    <Text typo="body 2" className={classes.userDataTitle}>
                      E-mail:{" "}
                    </Text>{" "}
                    <Text typo="label 2">{userInDialog ? userInDialog?.email : ""}</Text>
                  </span>
                  <span className={classes.userDataText}>
                    <Text typo="body 2" className={classes.userDataTitle}>
                      Added in:{" "}
                    </Text>{" "}
                    <Text typo="label 2">{userInDialog ? userInDialog?.Added : ""}</Text>
                  </span>
                  <span className={classes.userDataText}>
                    <Text typo="body 2" className={classes.userDataTitle}>
                      Last Active:{" "}
                    </Text>{" "}
                    <Text typo="label 2">3 days ago</Text>
                  </span>
                  <span className={classes.userDataText}>
                    <Text typo="body 2" className={classes.userDataTitle}>
                      Organisation role:{" "}
                    </Text>{" "}
                    <Text typo="label 2">{userInDialog ? userInDialog?.role : ""}</Text>
                  </span>
                </div>
                <Table minWidth="100%" rows={extensionRows} columnNames={extensionColumns} />
              </div>
            ),
          }}
        />
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
      <Modal
        width="444px"
        open={ismodalVisible}
        changeOpen={setModalVisible}
        action={
          <>
            <Button onClick={() => setModalVisible(false)} variant="noBorder">
              CANCEL
            </Button>
            <Button onClick={() => setModalVisible(false)} variant="noBorder">
              CONFIRM
            </Button>
          </>
        }
        header={
          <Text className={classes.modalHeader} typo="object heading">
            <Icon iconId="warn" iconVariant="focus" /> Attention
          </Text>
        }>
        <Text typo="body 1">
          By removing a user they won&apos;t be able to access any projects under your organisation
        </Text>
      </Modal>
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
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
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
  userDataContainer: {
    border: `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}`,
    padding: theme.spacing(3),
    borderRadius: 4,
  },
  userDataText: {
    display: "flex",
    gap: theme.spacing(1),
    alignItems: "center",
    marginBottom: theme.spacing(2),
  },
  userDataTitle: {
    fontWeight: "800",
  },
  formInputs: {
    marginTop: theme.spacing(3),
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(2),
  },
  modalHeader: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
  },
  buttonSmall: {
    padding: "3px 10px",
  },
}));

export default ManageUsers;
