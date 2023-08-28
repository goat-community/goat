import React from "react";

import Box from "@p4b/ui/components/Box";
import { Icon, Text } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface IEditFolderMenuProps {
  openEditModal: () => void;
  deleteFolderHandler: () => void;
}

const EditFolderMenu = (props: IEditFolderMenuProps) => {
  const { openEditModal, deleteFolderHandler } = props;

  const { classes } = useStyles();

  return (
    <Box className={classes.container}>
      <Box className={classes.row} onClick={openEditModal}>
        <Icon size="small" iconId="edit" className={classes.icon} />
        <Text typo="body 1">Edit</Text>
      </Box>
      <Box className={classes.row} onClick={deleteFolderHandler}>
        <Icon size="small" iconId="delete" className={classes.icon} />
        <Text typo="body 1">Delete</Text>
      </Box>
    </Box>
  );
};

const useStyles = makeStyles({ name: { EditFolderMenu } })((theme) => ({
  container: {
    padding: "5px",
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    padding: `${theme.spacing(1)}px ${theme.spacing(3)}px`,
    cursor: "pointer",
    "&:hover": {
      backgroundColor: `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}80`,
    },
  },
  icon: {
    opacity: 0.5,
  },
}));

export default EditFolderMenu;