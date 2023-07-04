import { useState } from "react";

import { makeStyles } from "../../../lib/ThemeProvider";
import { FileManagementTable, Chip } from "../../DataDisplay";
import Dialog from "../../Dialog";
import Modal from "../../Modal";
import { Card } from "../../Surfaces";
import { Icon, Text, IconButton, Button } from "../../theme";
import DashboardLayout from "../DashboardLayout";
import ContentInfoModal from "./components/ContentInfoModal";
import HeaderCard from "./components/HeaderCard";
import MoreMenu from "./components/MoreMenu";
import TreeViewFilter from "./components/TreeViewFilter";

const ContentManagement = () => {
  const { classes } = useStyles();
  const [modalContent, setModalContent] = useState<object | null>(null);
  const [dialogContent, setDialogContent] = useState<object | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

  const rows = [
    {
      name: (
        <span className={classes.folder}>
          <span className={classes.icon}>
            <Icon iconId="folder" />
          </span>
          Report_Final_Version
        </span>
      ),
      type: <Chip label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Report_Final_Version",
      type: <Chip label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Report_Final_Version",
      type: <Chip label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
  ];

  const columnNames = [
    {
      id: "name",
      label: "Name",
      numeric: false,
    },
    {
      id: "type",
      label: "Type",
      numeric: false,
    },
    {
      id: "modified",
      label: "Modified",
      numeric: false,
    },
    {
      id: "size",
      label: "Size",
      numeric: false,
    },
  ];

  const sampleModalData = [
    {
      tag: "Owner",
      data: "User name owner",
    },
    {
      tag: "Shared with",
      data: "team name, team name, ...",
    },
    {
      tag: "Type",
      data: "Datat table",
    },
    {
      tag: "Modified",
      data: "30.02.2022 20:30",
    },
    {
      tag: "Size",
      data: "30Kb",
    },
    {
      tag: "Location",
      data: "content/project/folderx",
    },
  ];

  const ContainingProjects = [
    {
      name: "Proposal_Budget_Revision",
      link: "/home",
    },
    {
      name: "FINAL_Project1",
      link: "/home",
    },
    {
      name: "Revision123",
      link: "/home",
    },
  ];

  const modal = modalContent
    ? {
        header: (
          <div className={classes.modalHeader}>
            <Text typo="section heading">Info</Text>
            <IconButton onClick={() => setModalContent(null)} iconId="close" />
          </div>
        ),
        body: <ContentInfoModal containingProjects={ContainingProjects} sampleModalData={sampleModalData} />,
        action: (
          <div className={classes.buttons}>
            <Button variant="noBorder">VIEW</Button>
            <Button variant="noBorder" onClick={() => setModalContent(null)}>
              CANCEL
            </Button>
          </div>
        ),
      }
    : null;

  const dialog = {
    width: "133px",
    body: <MoreMenu />,
  };

  function closeTablePopover() {
    setAnchorEl(null);
    setDialogContent(null);
  }

  return (
    <DashboardLayout>
      <HeaderCard />
      <div className={classes.container}>
        <TreeViewFilter />
        <Card noHover={true} className={classes.tableCard}>
          <FileManagementTable
            hover={true}
            columnNames={columnNames}
            rows={rows}
            modal={modal}
            setDialogAnchor={setAnchorEl}
            openDialog={setDialogContent}
            openModal={setModalContent}
          />
          {anchorEl ? (
            <Dialog
              anchorEl={anchorEl}
              className={classes.moreInfoDialog}
              onClick={closeTablePopover}
              // title={dialog ? dialog.title : undefined}
              width={dialog?.width ? dialog.width : "444px"}
              direction="right"
              // action={dialog?.action}
            >
              {dialog ? dialog.body : ""}
            </Dialog>
          ) : null}
          {modal && modalContent ? (
            <Modal
              width="444px"
              open={modalContent ? true : false}
              changeOpen={() => setModalContent(null)}
              header={modal.header}
              action={modal.action}>
              {modal.body}
            </Modal>
          ) : null}
        </Card>
      </div>
    </DashboardLayout>
  );
};

const useStyles = makeStyles({ name: { DashboardLayout } })((theme) => ({
  container: {
    display: "flex",
    gap: theme.spacing(3),
  },
  buttonTable: {
    fontSize: "12px",
    padding: "2px",
  },
  treeView: {
    padding: theme.spacing(3),
  },
  tableCard: {
    flexGrow: "1",
    padding: theme.spacing(3),
  },
  folder: {
    display: "flex",
    gap: theme.spacing(2),
  },
  icon: {
    opacity: 0.5,
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  modalListItem: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    paddingBottom: theme.spacing(3),
  },
  modalListItemTitle: {
    fontWeight: "800",
  },
  modalListItemData: {
    color: `${theme.colors.palette[theme.isDarkModeEnabled ? "light" : "dark"].main}80`,
  },
  modalSectionTitle: {
    fontWeight: "800",
    paddingBottom: theme.spacing(3),
  },
  divider: {
    margin: `0px 0px ${theme.spacing(3)}px 0px`,
  },
  projectText: {
    padding: `0px ${theme.spacing(3)}px`,
    paddingBottom: theme.spacing(3),
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  openLink: {
    textDecoration: "none",
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
  },
  inputModal: {
    "&.css-1umu3ji-MuiInputBase-input-MuiOutlinedInput-input": {
      padding: "0px",
    },
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
  },
  moreInfoDialog: {
    padding: "0px",
  },
}));

export default ContentManagement;
