import React, { useState } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { Divider } from "../../../DataDisplay";
import { TextField } from "../../../Inputs";
import { Icon, Text, IconButton } from "../../../theme";

interface ContentInfoModalProps {
  sampleModalData: {
    tag: string;
    data: string;
  }[];
  containingProjects: {
    name: string;
    link: string;
  }[];
}

const ContentInfoModal = (props: ContentInfoModalProps) => {
  const { sampleModalData, containingProjects } = props;

  const { classes } = useStyles();

  // Component States
  const [editMode, setEditMode] = useState(false);

  return (
    <div>
      <div className={classes.modalListItem} style={{ paddingBottom: "4px" }}>
        {editMode ? (
          <>
            <span style={{ display: "flex", alignItems: "center" }}>
              <TextField
                label=""
                defaultValue="Study1_3994"
                size="small"
                className={classes.inputWrapper}
                InputPropsClass={{
                  className: classes.inputModal,
                }}
              />
              .xml
            </span>
            <span>
              <IconButton
                onClick={() => setEditMode(!editMode)}
                type="submit"
                iconId="noBgCheck"
                size="small"
                className={classes.icon}
                iconVariant="focus"
              />
              <IconButton
                onClick={() => setEditMode(!editMode)}
                type="submit"
                iconId="close"
                size="small"
                iconVariant="error"
              />
            </span>
          </>
        ) : (
          <>
            <Text typo="body 2" className={classes.modalListItemTitle}>
              Study1_3994.xml{" "}
            </Text>
            <IconButton onClick={() => setEditMode(!editMode)} type="submit" iconId="edit" size="small" />
          </>
        )}
      </div>
      <Divider width="100%" color="gray" className={classes.divider} />
      {sampleModalData.map((data, indx) => (
        <div className={classes.modalListItem} key={v4()}>
          <Text typo="body 2" className={classes.modalListItemTitle}>
            {data.tag}:{" "}
          </Text>
          <Text typo="body 2" className={classes.modalListItemData}>
            {data.data}
          </Text>
        </div>
      ))}
      <Divider width="100%" color="gray" className={classes.divider} />
      <Text typo="body 2" className={classes.modalSectionTitle}>
        Containing Projects
      </Text>
      {containingProjects.map((data) => (
        <>
          <div className={classes.projectText}>
            <Text typo="body 2">{data.name}</Text>
            <a href={data.link} className={classes.openLink}>
              <Text typo="body 2" color="focus">
                Open
              </Text>
              <Icon iconId="open" size="small" />
            </a>
          </div>
          <Divider width="100%" color="gray" className={classes.divider} />
        </>
      ))}
    </div>
  );
};

const useStyles = makeStyles({ name: { ContentInfoModal } })((theme) => ({
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
    "&.MuiInputBase-input": {
      padding: `0px ${theme.spacing(2)}px`,
    },
    width: "150px",
  },
  inputWrapper: {
    marginRight: theme.spacing(1),
  },
  icon: {
    color: "green",
  },
  iconWrapper: {},
}));

export default ContentInfoModal;
