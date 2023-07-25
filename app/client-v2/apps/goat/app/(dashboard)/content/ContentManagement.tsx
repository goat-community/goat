"use client";

import GridContainer from "@/components/grid/GridContainer";
import SingleGrid from "@/components/grid/SingleGrid";
import { useState } from "react";

import { FileManagementTable, Chip } from "@p4b/ui/components/DataDisplay";
import Dialog from "@p4b/ui/components/Dialog";
import Modal from "@p4b/ui/components/Modal";
import { Card } from "@p4b/ui/components/Surfaces";
import { Icon, Text, IconButton, Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

import ContentInfoModal from "./ContentInfoModal";
import HeaderCard from "./HeaderCard";
import MoreMenu from "./MoreMenu";
import TreeViewFilter from "./TreeViewFilter";

const ContentManagement = () => {
  const { classes } = useStyles();
  const [modalContent, setModalContent] = useState<object | null>(null);
  const [dialogContent, setDialogContent] = useState<{
    name: React.ReactNode;
    type: React.ReactNode;
    modified: string;
    size: string;
  } | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [path, setPath] = useState<string[]>(["home"]);

  // Dumb Data
  // These are the rows of the table, it is only temporary for now
  const rows = [
    {
      name: (
        <Text className={classes.folder} typo="body 2">
          <span className={classes.icon}>
            <Icon iconId="folder" />
          </span>
          Report_Final_Version
        </Text>
      ),
      type: <Chip className={classes.chip} label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
      path: ["home"],
      stringName: "Report_Final_Version",
      files: [
        {
          name: "Project_XYZ_Conclusion",
          type: <Chip className={classes.chip} label="Project" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "Report_Final_Version"],
        },
        {
          name: "Data_Analysis_2023_Q1",
          type: <Chip className={classes.chip} label="Image" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "Report_Final_Version"],
        },
        {
          name: "Experiment_Results_Phase2",
          type: <Chip className={classes.chip} label="Report" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "Report_Final_Version"],
        },
      ],
    },
    {
      name: (
        <Text className={classes.folder} typo="body 2">
          <span className={classes.icon}>
            <Icon iconId="folder" />
          </span>
          plan_4_better
        </Text>
      ),
      type: <Chip className={classes.chip} label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
      path: ["home"],
      stringName: "plan_4_better",
      files: [
        {
          name: "Project_XYZ_Conclusion",
          type: <Chip className={classes.chip} label="Project" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "plan_4_better"],
        },
        {
          name: "Data_Analysis_2023_Q1",
          type: <Chip className={classes.chip} label="Image" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "plan_4_better"],
        },
        {
          name: "Experiment_Results_Phase2",
          type: <Chip className={classes.chip} label="Report" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "plan_4_better"],
        },
      ],
    },
    {
      name: (
        <Text className={classes.folder} typo="body 2">
          <span className={classes.icon}>
            <Icon iconId="folder" />
          </span>
          example_proj
        </Text>
      ),
      type: <Chip className={classes.chip} label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
      path: ["home"],
      stringName: "example_proj",
      files: [
        {
          name: "Project_XYZ_Conclusion",
          type: <Chip className={classes.chip} label="Project" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "example_proj"],
        },
        {
          name: (
            <Text className={classes.folder} typo="body 2">
              <span className={classes.icon}>
                <Icon iconId="folder" />
              </span>
              april_2023
            </Text>
          ),
          type: <Chip className={classes.chip} label="Layer" textDesign="italic" variant="Border" />,
          modified: "23 Jun 19",
          size: "30 kb",
          path: ["home", "example_proj"],
          stringName: "april_2023",
          files: [
            {
              name: "Project_XYZ_Conclusion",
              type: <Chip className={classes.chip} label="Project" textDesign="italic" variant="Border" />,
              modified: "23 Jun 19",
              size: "30 kb",
              path: ["home", "example_proj", "april_2023"],
            },
            {
              name: "Data_Analysis_2023_Q1",
              type: <Chip className={classes.chip} label="Image" textDesign="italic" variant="Border" />,
              modified: "23 Jun 19",
              size: "30 kb",
              path: ["home", "example_proj", "april_2023"],
            },
            {
              name: "Experiment_Results_Phase2",
              type: <Chip className={classes.chip} label="Report" textDesign="italic" variant="Border" />,
              modified: "23 Jun 19",
              size: "30 kb",
              path: ["home", "example_proj", "april_2023"],
            },
          ],
        },
      ],
    },
    {
      name: "Report_Final_Version",
      type: <Chip className={classes.chip} label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip className={classes.chip} label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip className={classes.chip} label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip className={classes.chip} label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Report_Final_Version",
      type: <Chip className={classes.chip} label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip className={classes.chip} label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip className={classes.chip} label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip className={classes.chip} label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      path: ["home"],
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

  // this is the Info Modal
  const modal = modalContent
    ? {
        header: (
          <div className={classes.modalHeader}>
            <Text typo="subtitle" className={classes.modalHeadertext}>
              Info
            </Text>
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

  // this is the MoreMenu Dialog
  const dialog = {
    width: "133px",
    body: <MoreMenu rowInfo={dialogContent} />,
  };

  function closeTablePopover() {
    setAnchorEl(null);
    setDialogContent(null);
  }

  return (
    <>
      <GridContainer>
        <SingleGrid span={4}>
          <HeaderCard path={path} setPath={setPath} />
        </SingleGrid>
      </GridContainer>
      <GridContainer>
        <SingleGrid span={1}>
          <TreeViewFilter />
        </SingleGrid>
        <SingleGrid span={3}>
          <Card noHover={true} className={classes.tableCard}>
            <FileManagementTable
              hover={true}
              columnNames={columnNames}
              rows={rows}
              modal={modal}
              setDialogAnchor={setAnchorEl}
              openDialog={setDialogContent}
              openModal={setModalContent}
              currPath={path}
              setPath={setPath}
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
        </SingleGrid>
      </GridContainer>
    </>
  );
};

const useStyles = makeStyles({ name: { ContentManagement } })((theme) => ({
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
  modalHeadertext: {
    fontWeight: "500",
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
  chip: {
    height: "auto",
    fontSize: "12px",
    "& .css-6od3lo-MuiChip-label": {
      padding: "3px 0px",
    },
    "& .mui-6od3lo-MuiChip-label": {
      padding: "0px 10px",
    },
    margin: "12px 0px",
    padding: "3px 0px",
  },
}));

export default ContentManagement;
