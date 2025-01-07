import { Box, Button, TextField, Typography } from "@mui/material";
import { useState } from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

interface CopyFieldProps {
  label?: string;
  value?: string;
  onCopy?: (value: string) => void;
  copyTimeout?: number;
  copyText?: string;
  copiedText?: string;
  buttonWidth?: string;
}

const CopyField: React.FC<CopyFieldProps> = ({
  label,
  value = "",
  onCopy,
  copyTimeout = 2000,
  copyText = "Copy",
  copiedText = "Copied",
  buttonWidth = "200px",
}) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = () => {
    if (isCopied) return;
    navigator.clipboard
      .writeText(value)
      .then(() => {
        if (onCopy) onCopy(value);
        setIsCopied(true);

        // Reset the button back to "Copy" after a short delay
        setTimeout(() => setIsCopied(false), copyTimeout);
      })
      .catch((err) => console.error("Failed to copy text: ", err));
  };

  return (
    <Box display="flex" alignItems="center">
      <TextField
        size="small"
        label={label}
        value={value}
        variant="outlined"
        fullWidth
        InputProps={{ readOnly: true }}
        sx={{ mr: 4 }}
      />
      <Button
        variant={isCopied ? "contained" : "outlined"}
        color="primary"
        disableElevation
        onClick={handleCopy}
        startIcon={<Icon iconName={ICON_NAME.LINK} style={{ fontSize: "16px" }} />}
        sx={{ width: buttonWidth }}>
        <Typography variant="body2" fontWeight="bold" color="inherit">
          {isCopied ? copiedText : copyText}
        </Typography>
      </Button>
    </Box>
  );
};

export default CopyField;
