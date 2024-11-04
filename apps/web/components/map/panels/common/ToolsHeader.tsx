import { IconButton, Stack, Typography } from "@mui/material";
import React from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

interface ToolsHeaderProps {
  onBack: () => void;
  title: string;
  docs?: string;
}

const ToolsHeader: React.FC<ToolsHeaderProps> = ({ onBack, title, docs }) => {
  return (
    <Stack direction="row" alignItems="center" spacing={2}>
      <IconButton onClick={onBack}>
        <Icon iconName={ICON_NAME.CHEVRON_LEFT} style={{ fontSize: "15px" }} />
      </IconButton>
      <Typography
        variant="body1"
        fontWeight="bold"
        sx={{
          display: "flex",
        }}>
        {title}
      </Typography>
      {docs && (
        <IconButton onClick={() => window.open(docs, "_blank")}>
          <Icon iconName={ICON_NAME.BOOK} style={{ fontSize: "12px" }} />
        </IconButton>
      )}
    </Stack>
  );
};

export default ToolsHeader;
