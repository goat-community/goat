"use client";

import EditFolderMenu from "@/app/[lng]/(dashboard)/content/EditFolderMenu";
import HeaderCard from "@/app/[lng]/(dashboard)/content/HeaderCard";
import MoreMenu from "@/app/[lng]/(dashboard)/content/MoreMenu";
import TreeViewFilter from "@/app/[lng]/(dashboard)/content/TreeViewFilter";
import GridContainer from "@/components/grid/GridContainer";
import SingleGrid from "@/components/grid/SingleGrid";
import ContentInfoModal from "@/components/modals/ContentInfoModal";
import { API } from "@/lib/api/apiConstants";
import {
  addFolderService,
  addLayerService,
  contentFoldersFetcher,
  contentLayersFetcher,
  contentProjectsFetcher,
  contentReportsFetcher,
  deleteFolderService,
  deleteLayerService,
  updateFolderService,
} from "@/lib/services/dashboard";
import { formatDate } from "@/lib/utils/helpers";
import FolderIcon from "@mui/icons-material/Folder";
import { useRouter } from "next/navigation";
import React, {useCallback, useEffect, useState} from "react";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

import { FileManagementTable, Chip } from "@p4b/ui/components/DataDisplay";
import Dialog from "@p4b/ui/components/Dialog";
import { TextField } from "@p4b/ui/components/Inputs";
import Modal from "@p4b/ui/components/Modal";
import { Card } from "@p4b/ui/components/Surfaces";
import { Text, IconButton, Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {ISelectedFolder} from "@/types/dashboard/content";
import type {IDashboardTableRowInfo} from "@/types/dashboard/content";

const columnNames = [
  {
    id: "name",
    label: "",
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

interface ModalContent {
  id: string;
  name: string;
  chip: React.ReactNode;
  modified: string,
  path: string[],
  size: string,
  label: string,
  info: {
    tag: string;
    data: string;
  }[];
}

interface IRow {
  id: string,
  name: string,
  chip: React.ReactNode,
  modified: string,
  path: string[],
  size: string,
  label: string,
  info: object[],
  feature_layer_type?: string,
  type?: string
}


const ContentManagement = () => {
  const {
    data: folderData,
    mutate: getFoldersMutation,
  } = useSWR(API.folder, contentFoldersFetcher);
  const { data: layerData, trigger: layerTrigger } = useSWRMutation(API.layer, contentLayersFetcher);
  const { data: reportData, trigger: reportTrigger } = useSWRMutation(API.report, contentReportsFetcher);
  const { data: projectData, trigger: projectTrigger } = useSWRMutation(API.project, contentProjectsFetcher);

  const [modalContent, setModalContent] = useState<ModalContent | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [folderAnchorData, setFolderAnchorData] = useState<({ anchorEl: EventTarget & HTMLButtonElement; folder: ISelectedFolder }) | null>(null);
  const [path, setPath] = useState<string[]>(["home"]);
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<ISelectedFolder | null>(null);
  const [openEditFolderModal, setOpenEditFolderModal] = useState<boolean>(false);
  const [openAddFolderModal, setOpenAddFolderModal] = useState<boolean>(false);
  const [editedFolderName, setEditedFolderName] = useState<string>("");
  const [addedFolderName, setAddedFolderName] = useState<string>("");
  const [rows, setRows] = useState<IRow[]>([]);
  const [dialogContent, setDialogContent] = useState<IDashboardTableRowInfo | null>(null);

  const { classes } = useStyles();
  const router = useRouter();

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
        body: <ContentInfoModal sampleModalData={modalContent.info} />,
        action: (
          <div className={classes.buttons}>
            {modalContent.label === "layer" ? (
              <Button variant="noBorder" onClick={() => router.push(`/content/preview/${modalContent?.id}`)}>
                VIEW
              </Button>
            ) : null}
            <Button variant="noBorder" onClick={() => setModalContent(null)}>
              CANCEL
            </Button>
          </div>
        ),
      }
    : null;

  // this is the Edit folder Modal
  const editModalContent = openEditFolderModal
    ? {
        header: (
          <div className={classes.modalHeader}>
            <Text typo="subtitle" className={classes.modalHeaderText}>
              Edit
            </Text>
            <IconButton onClick={closeEditeModal} iconId="close" />
          </div>
        ),
        body: (
          <TextField
            className={classes.width100}
            onValueBeingTypedChange={({ value }) => {
              setEditedFolderName(value);
            }}
          />
        ),
        action: (
          <div className={classes.buttons}>
            <Button variant="noBorder" onClick={updateFolderHandler}>
              SAVE
            </Button>
            <Button variant="noBorder" onClick={closeEditeModal}>
              CANCEL
            </Button>
          </div>
        ),
      }
    : null;

  const addFolderModalContent = openAddFolderModal
    ? {
        header: (
          <div className={classes.modalHeader}>
            <Text typo="subtitle" className={classes.modalHeaderText}>
              Add new folder
            </Text>
            <IconButton onClick={closeAddFolderModal} iconId="close" />
          </div>
        ),
        body: (
          <TextField
            className={classes.width100}
            onValueBeingTypedChange={({ value }) => {
              setAddedFolderName(value);
            }}
          />
        ),
        action: (
          <div className={classes.buttons}>
            <Button variant="noBorder" onClick={addFolderHandler}>
              SAVE
            </Button>
            <Button variant="noBorder" onClick={closeAddFolderModal}>
              CANCEL
            </Button>
          </div>
        ),
      }
    : null;

  const getContentByFolder = useCallback((id: string) => {
    layerTrigger(id);
    projectTrigger(id);
    reportTrigger(id);
  }, [layerTrigger, projectTrigger, reportTrigger]);

  function closeTablePopover() {
    setAnchorEl(null);
    setDialogContent(null);
  }

  function closeFolderPopover() {
    setFolderAnchorData(null);
  }

  function handleSelectFolder(folder) {
    setSelectedFolder(folder);
    getContentByFolder(folder.id);
  }

  async function deleteFolderHandler() {
    if (folderAnchorData?.folder?.id) {
      await deleteFolderService(API.folder, folderAnchorData.folder.id);
      closeFolderPopover();
      await getFoldersMutation();
      setSelectedFolder(null);
    }
  }

  async function updateFolderHandler() {
    if (folderAnchorData?.folder?.id) {
      await updateFolderService(API.folder, folderAnchorData.folder.id, {name: editedFolderName});
      closeFolderPopover();
      setOpenEditFolderModal(false);
      await getFoldersMutation();
    }
  }

  async function addFolderHandler() {
    await addFolderService(API.folder, { name: addedFolderName });
    setOpenAddFolderModal(false);
    await getFoldersMutation();
  }

  function closeEditeModal() {
    setOpenEditFolderModal(false);
    setEditedFolderName("");
    closeFolderPopover();
  }

  function closeAddFolderModal() {
    setOpenAddFolderModal(false);
    setAddedFolderName("");
  }

  async function addLayer(body) {
    const res = await addLayerService(API.layer, body);
    await layerTrigger(res.folder_id);
  }

  async function handleDeleteItem(data) {
    await deleteLayerService(API[data.label], data.id);
    getContentByFolder(data.folder_id);
  }

  useEffect(() => {
    let filteredRows: IRow[] = [];

    if (layerData?.items) {
      filteredRows.push(
        ...layerData.items.map((item) => {
          return {
            ...item,
            id: item.id,
            name: item?.name,
            chip: <Chip className={classes.chip} label="layer" textDesign="italic" variant="Border" />,
            modified: formatDate(item?.metadata?.updated_at, "DD MMM YY"),
            path: ["home"],
            size: `${item?.metadata?.size || ""} kb`,
            label: "layer",
            info: [
              {
                tag: "Name",
                data: item?.name,
              },
              {
                tag: "Description",
                data: item?.description,
              },
              {
                tag: "Type",
                data: item?.type,
              },
              {
                tag: "Modified",
                data: item?.updated_at,
              },
              {
                tag: "Size",
                data: `${item?.metadata?.size || ""} kb`,
              },
            ],
          };
        })
      );
    }

    if (projectData?.items) {
      filteredRows.push(
        ...projectData?.items?.map((item) => {
          return {
            ...item,
            id: item.id,
            name: item?.name,
            chip: <Chip className={classes.chip} label="project" textDesign="italic" variant="Border" />,
            modified: formatDate(item?.metadata?.updated_at, "DD MMM YY"),
            path: ["home"],
            size: `${item?.metadata?.size || ""} kb`,
            label: "project",
            info: [
              {
                tag: "Name",
                data: item?.name,
              },
              {
                tag: "Description",
                data: item?.description,
              },
              {
                tag: "Type",
                data: item?.type,
              },
              {
                tag: "Modified",
                data: item?.updated_at,
              },
              {
                tag: "Size",
                data: `${item?.metadata?.size || ""} kb`,
              },
            ],
          };
        })
      );
    }

    if (reportData?.items) {
      filteredRows.push(
        ...reportData?.items?.map((item) => {
          return {
            ...item,
            id: item.id,
            name: item?.name,
            chip: <Chip className={classes.chip} label="report" textDesign="italic" variant="Border" />,
            modified: formatDate(item?.metadata?.updated_at, "DD MMM YY"),
            path: ["home"],
            size: `${item?.metadata?.size || ""} kb`,
            label: "report",
            info: [
              {
                tag: "Name",
                data: item?.name,
              },
              {
                tag: "Description",
                data: item?.description,
              },
              {
                tag: "Type",
                data: item?.type,
              },
              {
                tag: "Modified",
                data: item?.updated_at,
              },
              {
                tag: "Size",
                data: `${item?.metadata?.size || ""} kb`,
              },
            ],
          };
        })
      );
    }

    if (selectedFilters.length > 0) {
      filteredRows = filteredRows.filter(
        (item) =>
          selectedFilters.includes(item.label) ||
          (item.feature_layer_type && selectedFilters.includes(item.feature_layer_type)) ||
          (item.type && selectedFilters.includes(item.type))
      );
    }

    setRows(filteredRows);
  }, [selectedFilters, projectData, layerData, reportData, classes.chip]);

  useEffect(() => {
    if (folderData?.items[0] && selectedFolder === null) {
      setSelectedFolder(folderData.items[0]);
      getContentByFolder(folderData.items[0].id);
    }
  }, [folderData?.items, selectedFolder, getContentByFolder]);

  return (
    <>
      <GridContainer>
        <SingleGrid span={4}>
          <HeaderCard path={path} setPath={setPath} selectedFolder={selectedFolder} addLayer={addLayer} />
        </SingleGrid>
      </GridContainer>
      <GridContainer>
        <SingleGrid span={1}>
          <Card className={classes.treeView} noHover={true} width="100%">
            <TreeViewFilter
              folderData={folderData?.items}
              projectData={projectData?.items}
              layerData={layerData?.items}
              reportData={reportData?.items}
              handleSelectFolder={handleSelectFolder}
              selectedFilters={selectedFilters}
              setSelectedFilters={setSelectedFilters}
              handleAddFolder={() => setOpenAddFolderModal(true)}
              setFolderAnchorData={setFolderAnchorData}
              setSelectedFolder={setSelectedFolder}
            />
            {folderAnchorData ? (
              <Dialog
                anchorEl={folderAnchorData.anchorEl}
                className={classes.moreInfoDialog}
                onClick={closeFolderPopover}
                width="150px"
                direction="right">
                <EditFolderMenu
                  openEditModal={() => setOpenEditFolderModal(true)}
                  deleteFolderHandler={deleteFolderHandler}
                />
              </Dialog>
            ) : null}
          </Card>
        </SingleGrid>
        <SingleGrid span={3}>
          <Card noHover={true} className={classes.tableCard}>
            <FileManagementTable
              hover={true}
              columnNames={columnNames}
              rows={rows}
              setDialogAnchor={setAnchorEl}
              setDialogContent={setDialogContent}
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
                <MoreMenu rowInfo={dialogContent} handleDeleteItem={handleDeleteItem} />
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
            {editModalContent ? (
              <Modal
                width="444px"
                open={!!editModalContent}
                changeOpen={closeEditeModal}
                header={editModalContent.header}
                action={editModalContent.action}>
                {editModalContent.body}
              </Modal>
            ) : null}
            {addFolderModalContent ? (
              <Modal
                width="444px"
                open={!!addFolderModalContent}
                changeOpen={closeAddFolderModal}
                header={addFolderModalContent.header}
                action={addFolderModalContent.action}>
                {addFolderModalContent.body}
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
  width100: {
    width: "100%",
  },
}));

export default ContentManagement;
