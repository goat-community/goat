import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

interface ConfirmDialogProps {
  title: string;
  body;
  open: boolean;
  closeText?: string;
  onClose?: () => void;
  confirmText?: string;
  onConfirm?: () => void;
  matchText?: string;
}

const ConfirmModal: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  body,
  closeText,
  onClose,
  confirmText,
  onConfirm,
  matchText,
}) => {
  const [matchTextValue, setMatchTextValue] = useState("");

  return (
    <Dialog
      open={open}
      onClose={() => {
        if (matchText) {
          setMatchTextValue("");
        }
        onClose?.();
      }}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{body}</DialogContentText>
        {matchText && (
          <TextField
            required
            fullWidth
            placeholder={matchText}
            id="matchText"
            onChange={(e) => setMatchTextValue(e.target.value)}
            value={matchTextValue}
            sx={{ my: 4 }}
          />
        )}
      </DialogContent>
      <DialogActions
        disableSpacing
        sx={{
          pb: 2,
        }}>
        <Button onClick={onClose} variant="text">
          <Typography variant="body2" fontWeight="bold">
            {closeText || "Close"}
          </Typography>
        </Button>
        <Button
          onClick={onConfirm}
          variant="text"
          color="error"
          disabled={!!matchText && matchTextValue !== matchText}>
          <Typography variant="body2" fontWeight="bold" color="inherit">
            {confirmText || "Confirm"}
          </Typography>
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmModal;
