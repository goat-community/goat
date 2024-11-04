import { Stack, Typography, useTheme } from "@mui/material";
import React from "react";

import type { ICON_NAME } from "@p4b/ui/components/Icon";
import { Icon } from "@p4b/ui/components/Icon";

type Props = {
  icon: ICON_NAME;
  label: string;
};

const EmptySection: React.FC<Props> = ({ icon, label }) => {
  const theme = useTheme();

  return (
    <Stack
      direction="column"
      spacing={4}
      sx={{
        mt: 10,
        textAlign: "center",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100%",
      }}>
      <Icon iconName={icon} htmlColor={theme.palette.text.secondary} />
      <Typography variant="h6" color={theme.palette.text.secondary}>
        {label}
      </Typography>
    </Stack>
  );
};

export default EmptySection;
