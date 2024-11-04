import { Box, Modal as MUIModal, useTheme } from "@mui/material";
import React, { forwardRef, memo } from "react";

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

    const theme = useTheme();

    // Functions
    const handleClose = () => changeOpen(false);

    return (
      <MUIModal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description">
        <Box
          sx={{
            position: "absolute",
            borderRadius: theme.spacing(1),
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: width,
            boxShadow: "24",
            backgroundColor: theme.palette.background.paper,
            padding: `${theme.spacing(5)} ${theme.spacing(5)}`,
            [theme.breakpoints.down("sm")]: {
              width: "90%",
            },
          }}>
          {header ? <Box sx={{ paddingBottom: theme.spacing(3) }}>{header}</Box> : null}
          <div>{children}</div>
          {action ? <Box sx={{ paddingBottom: theme.spacing(3) }}>{action}</Box> : null}
        </Box>
      </MUIModal>
    );
  })
);

export default Modal;
