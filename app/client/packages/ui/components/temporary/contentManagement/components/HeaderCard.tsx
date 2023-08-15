import { useState } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../../../../lib/ThemeProvider";
import Modal from "../../../Modal";
import { ToggleTabs } from "../../../Navigation";
import { Card } from "../../../Surfaces";
import { Button, Text, IconButton } from "../../../theme";
import CreateContent from "./CreateContent";

interface HeaderCardProps {
  path: string[];
  setPath: (value: string[]) => void;
}

const HeaderCard = (props: HeaderCardProps) => {
  const { path, setPath } = props;

  const { classes } = useStyles();
  const [value, setValue] = useState<string | null>("formatLeft");
  const [addContent, setAddContent] = useState(false);

  function handlePathChange(indx: number) {
    const newPath = [...path];
    setPath(newPath.slice(0, indx + 1));
  }

  return (
    <Card noHover={true} width="100%" className={classes.headerCard}>
      <div className={classes.headerContainer}>
        <div className={classes.headerPath}>
          <Text typo="section heading" className={classes.headerText}>
            Content
          </Text>
          <span style={{ display: "flex", alignItems: "center" }}>
            <span className={classes.path}>
              {path.map((singlePath, indx) => (
                <span key={v4()} className={classes.path}>
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
          <span style={{ display: "flex", gap: "10px" }}>
            <Button variant="noBorder" startIcon="newFolder">
              New folder
            </Button>
            <Button
              variant="noBorder"
              className={classes.headerText}
              onClick={() => setAddContent(true)}
              startIcon="newFile">
              Add content
            </Button>
          </span>
          <ToggleTabs
            defaultValue={value}
            onResultChange={setValue}
            tabs={[
              {
                iconId: "formatLeft",
                value: "formatLeft",
              },
              {
                iconId: "viewModul",
                value: "viewModul",
              },
            ]}
          />
        </div>
      </div>
      <Modal
        width="444px"
        open={addContent}
        changeOpen={() => setAddContent(false)}
        header={
          <div className={classes.modalHeader}>
            <Text typo="section heading" className={classes.modalHeadertext}>
              Add content
            </Text>
            <IconButton onClick={() => setAddContent(false)} iconId="close" />
          </div>
        }>
        <CreateContent modalState={setAddContent} />
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
    width: "100%",
  },
  headerText: {
    fontWeight: 800,
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
  modalHeadertext: {
    fontWeight: "500",
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
}));

export default HeaderCard;
