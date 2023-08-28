import AddLayerManagement from "@/app/[lng]/(dashboard)/content/AddLayerManagement";
import CreateContent from "@/app/[lng]/(dashboard)/content/CreateContent";
import { useState } from "react";
import { v4 } from "uuid";

import Modal from "@p4b/ui/components/Modal";
import { Card } from "@p4b/ui/components/Surfaces";
import { Button, Text, IconButton, Icon } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type { ISelectedFolder } from "@/types/dashboard/content";

interface HeaderCardProps {
  selectedFolder: ISelectedFolder | null;
  path: string[];
  setPath: (value: string[]) => void;
  addLayer: (value: object) => void;
}

const HeaderCard = (props: HeaderCardProps) => {
  const { path, setPath, selectedFolder, addLayer } = props;

  const { classes } = useStyles();
  const [addContent, setAddContent] = useState<boolean>(false);
  const [addLayerMode, setAddLayerMode] = useState<boolean>(false);

  function handlePathChange(indx: number) {
    const newPath = [...path];
    setPath(newPath.slice(0, indx + 1));
  }

  return (
    <Card noHover={true} width="100%" className={classes.headerCard}>
      <div className={classes.headerContainer}>
        <div className={classes.headerPath}>
          <Text typo="page heading" className={classes.headerText}>
            Library
          </Text>
          <span style={{ display: "flex", alignItems: "center" }}>
            <span className={classes.path}>
              {path.map((singlePath, indx) => (
                <span key={v4()} className={classes.path}>
                  {indx === 0 ? <Icon iconId="home" size="small" iconVariant="gray" /> : null}
                  <Text
                    typo="body 2"
                    className={classes.pathFile}
                    color={indx === path.length - 1 ? "primary" : "secondary"}>
                    <span onClick={() => handlePathChange(indx)}>{singlePath}</span>
                  </Text>
                  {indx !== path.length - 1 ? <Text typo="body 2">/</Text> : null}
                </span>
              ))}
            </span>
          </span>
        </div>
        <div className={classes.headerActions}>
          <div style={{ display: "flex", gap: "10px" }}>
            <Button
              variant="noBorder"
              disabled={!selectedFolder}
              startIcon="newFile"
              onClick={() => setAddLayerMode(true)}>
              New layer
            </Button>
            <Button
              variant="noBorder"
              startIcon="newFolder"
              disabled={!selectedFolder}
              onClick={() => setAddContent(true)}>
              New project
            </Button>
          </div>
        </div>
      </div>
      <Modal
        width="444px"
        open={addContent}
        changeOpen={() => setAddContent(false)}
        header={
          <div className={classes.modalHeader}>
            <Text typo="section heading" className={classes.modalHeaderText}>
              Add content
            </Text>
            <IconButton onClick={() => setAddContent(false)} iconId="close" />
          </div>
        }>
        <CreateContent modalState={setAddContent} />
      </Modal>

      {/*Add Layer Modal*/}
      <Modal
        width="444px"
        open={addLayerMode}
        changeOpen={() => setAddLayerMode(false)}
        header={
          <div className={classes.modalHeader}>
            <Text typo="section heading" className={classes.modalHeaderText}>
              Add Layer
            </Text>
            <IconButton onClick={() => setAddLayerMode(false)} iconId="close" />
          </div>
        }>
        <AddLayerManagement
          selectedFolder={selectedFolder}
          setAddLayerMode={setAddLayerMode}
          addLayer={addLayer}
        />
      </Modal>
    </Card>
  );
};

const useStyles = makeStyles({ name: { HeaderCard } })((theme) => ({
  headerCard: {
    marginBottom: theme.spacing(3),
  },
  headerContainer: {
    padding: `${theme.spacing(2)}px ${theme.spacing(3)}px`,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  headerText: {
    fontWeight: 800,
    width: "29%",
    // width: "fit-content",
  },
  headerPath: {
    width: "60%",
    display: "flex",
    alignItems: "center",
    gap: "100px",
  },
  path: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
  },
  pathFile: {
    cursor: "pointer",
  },
  headerActions: {
    width: "40%",
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(5) + theme.spacing(3),
  },
  icon: {
    marginRight: "10px",
  },
  modalHeaderText: {
    fontWeight: "500",
    fontSize: "20px",
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
}));

export default HeaderCard;
