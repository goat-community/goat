"use client";

import ContentInfoModal from "@/app/[lng]/(dashboard)/content/ContentInfoModal";
import HeaderCard from "@/app/[lng]/(dashboard)/content/HeaderCard";
import MoreMenu from "@/app/[lng]/(dashboard)/content/MoreMenu";
import TreeViewFilter from "@/app/[lng]/(dashboard)/content/TreeViewFilter";
import GridContainer from "@/components/grid/GridContainer";
import SingleGrid from "@/components/grid/SingleGrid";
import { API } from "@/lib/api/apiConstants";
import {
  addLayerService,
  contentFoldersFetcher,
  contentLayersFetcher,
  contentProjectsFetcher,
  contentReportsFetcher,
} from "@/lib/services/dashboard";
import { formatDate } from "@/lib/utils/helpers";
import FolderIcon from "@mui/icons-material/Folder";
import React, { useEffect, useState } from "react";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

import { FileManagementTable, Chip } from "@p4b/ui/components/DataDisplay";
import Dialog from "@p4b/ui/components/Dialog";
import Modal from "@p4b/ui/components/Modal";
import { Card } from "@p4b/ui/components/Surfaces";
import { Text, IconButton, Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

//todo check
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

interface ModalContent {
  info: string;
}

interface SelectedFolder {
  name: string;
}

const ContentManagement = () => {
  const { data: folderData, error: folderError } = useSWR(API.folder, contentFoldersFetcher);
  const { data: layerData, trigger: layerTrigger } = useSWRMutation(API.layer, contentLayersFetcher);
  const { data: reportData, trigger: reportTrigger } = useSWRMutation(API.report, contentReportsFetcher);
  const { data: projectData, trigger: projectTrigger } = useSWRMutation(API.project, contentProjectsFetcher);

  const [modalContent, setModalContent] = useState<ModalContent | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [path, setPath] = useState<string[]>(["home"]);
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<SelectedFolder | null>(null);
  const [rows, setRows] = useState<any[]>([]);
  const [dialogContent, setDialogContent] = useState<{
    name: React.ReactNode;
    type: React.ReactNode;
    modified: string;
    size: string;
  } | null>(null);

  const { classes } = useStyles();

  const columnNames = [
    {
      id: "name",
      label: selectedFolder?.name || "",
      numeric: false,
      isSortable: false,
      icon: FolderIcon,
    },
    {
      id: "type",
      label: "Type",
      numeric: false,
      isSortable: true,
    },
    {
      id: "modified",
      label: "Modified",
      numeric: false,
      isSortable: true,
    },
    {
      id: "size",
      label: "Size",
      numeric: false,
      isSortable: true,
    },
  ];

  // this is the Info Modal
  const modal = modalContent
    ? {
        header: (
          <div className={classes.modalHeader}>
            <Text typo="subtitle" className={classes.modalHeaderText}>
              Info
            </Text>
            <IconButton onClick={() => setModalContent(null)} iconId="close" />
          </div>
        ),
        body: (
          <ContentInfoModal containingProjects={ContainingProjects} sampleModalData={modalContent.info} />
        ),
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

  function closeTablePopover() {
    setAnchorEl(null);
    setDialogContent(null);
  }

  function handleSelectFolder(folder) {
    setSelectedFolder(folder);
    layerTrigger(folder.id);
    projectTrigger(folder.id);
    reportTrigger(folder.id);
  }

  function handleAddFolder() {
    console.log("handleAddFolder");
  }

  async function addLayer(body) {
    const res = await addLayerService(API.layer, body);
    await layerTrigger(res.folder_id);
  }

  useEffect(() => {
    let filteredRows = [];

    if (layerData?.items) {
      filteredRows.push(
        ...layerData?.items?.map((item) => {
          return {
            id: item.id,
            name: item?.name,
            type: <Chip className={classes.chip} label="layer" textDesign="italic" variant="Border" />,
            modified: formatDate(item?.metadata?.updated_at, "DD MMM YY"),
            path: ["home"],
            size: `${item?.metadata?.size || ""} kb`,
            info: [],
          };
        })
      );
    }

    if (projectData?.items) {
      filteredRows.push(
        ...projectData?.items?.map((item) => {
          return {
            id: item.id,
            name: item?.name,
            type: <Chip className={classes.chip} label="project" textDesign="italic" variant="Border" />,
            modified: formatDate(item?.metadata?.updated_at, "DD MMM YY"),
            path: ["home"],
            size: `${item?.metadata?.size || ""} kb`,
            info: [],
          };
        })
      );
    }

    if (reportData?.items) {
      filteredRows.push(
        ...reportData?.items?.map((item) => {
          return {
            id: item.id,
            name: item?.name,
            type: <Chip className={classes.chip} label="report" textDesign="italic" variant="Border" />,
            modified: formatDate(item?.metadata?.updated_at, "DD MMM YY"),
            path: ["home"],
            size: `${item?.metadata?.size || ""} kb`,
            info: [],
          };
        })
      );
    }

    if (selectedFilters.length > 0) {
      filteredRows = filteredRows.filter((item) => selectedFilters.includes(item.id));
    }

    setRows(filteredRows);
  }, [selectedFilters, projectData, layerData, reportData]);

  useEffect(() => {
    if (folderData?.items[0] && selectedFolder === null) {
      setSelectedFolder(folderData.items[0]);
      layerTrigger(folderData.items[0].id);
      projectTrigger(folderData.items[0].id);
      reportTrigger(folderData.items[0].id);
    }
  }, [folderData?.items, selectedFolder]);

  return (
    <>
      <GridContainer>
        <SingleGrid span={4}>
          <HeaderCard path={path} setPath={setPath} selectedFolder={selectedFolder} addLayer={addLayer} />
        </SingleGrid>
      </GridContainer>
      <GridContainer>
        <SingleGrid span={1}>
          <TreeViewFilter
            folderData={folderData?.items}
            projectData={projectData?.items}
            layerData={layerData?.items}
            reportData={reportData?.items}
            handleSelectFolder={handleSelectFolder}
            selectedFilters={selectedFilters}
            setSelectedFilters={setSelectedFilters}
            handleAddFolder={handleAddFolder}
          />
        </SingleGrid>
        <SingleGrid span={3}>
          <Card noHover={true} className={classes.tableCard}>
            <FileManagementTable
              hover={true}
              columnNames={columnNames}
              rows={rows}
              setDialogAnchor={setAnchorEl}
              openDialog={setDialogContent}
              setModalContent={setModalContent}
              currPath={path}
              setPath={setPath}
            />
            {anchorEl ? (
              <Dialog
                anchorEl={anchorEl}
                className={classes.moreInfoDialog}
                onClick={closeTablePopover}
                // title={dialog ? dialog.title : undefined}
                width="150px"
                direction="right"
                // action={dialog?.action}
              >
                <MoreMenu rowInfo={dialogContent} />
              </Dialog>
            ) : null}
            {modal ? (
              <Modal
                width="444px"
                open={!!modal}
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
  modalHeaderText: {
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
