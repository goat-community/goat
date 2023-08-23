import { Modal as MUIModal } from "@mui/material";
import Box from "@mui/material/Box";
import React, { forwardRef, memo } from "react";

import { makeStyles } from "../lib/ThemeProvider";

export type ModalProps = {
  className?: string;
  children?: React.ReactNode;
  width: string;
  open: boolean;
  changeOpen: (value: boolean) => void;
  header?: React.ReactNode;
  action?: React.ReactNode;
};

const Modal = memo(
  forwardRef<HTMLElement, ModalProps>((props) => {
    const { width, children, open, changeOpen, header, action } = props;

    const { classes } = useStyles({ width });

    // Functions
    const handleClose = () => changeOpen(false);

    return (
      <MUIModal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description">
        <Box className={classes.box}>
          {header ? <div className={classes.header}>{header}</div> : null}
          <div>{children}</div>
          {action ? <div className={classes.action}>{action}</div> : null}
        </Box>
      </MUIModal>
    );
  })
);

const useStyles = makeStyles<{ width: string }>({
  name: { Modal },
})((theme, { width }) => ({
  box: {
    position: "absolute",
    borderRadius: theme.spacing(1),
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: width,
    boxShadow: "24",
    backgroundColor: theme.colors.useCases.surfaces.background,
    padding: `${theme.spacing(3)}px ${theme.spacing(5)}px`,
  },
  header: {
    paddingBottom: theme.spacing(3),
  },
  action: {
    paddingTop: theme.spacing(3),
    display: "flex",
    justifyContent: "end",
    alignItems: "center",
    gap: theme.spacing(3),
  },
}));

export default Modal;
